from datetime import datetime
from time import time
from sentry_sdk import add_breadcrumb, capture_exception, capture_message
from time import sleep
import boto3
import datetime
import json
import re
from sql.create_ftp_syntheticholdings import create_ftp_syntheticholdings_query, create_ftp_syntheticholdings_relative_date_query
from time import time
from sentry import init_sentry

green="\033[0;32m"
yellow="\033[0;33m"
off = "\033[0;37m" #dark grey as happy medium between light- and dark- mode.
red = "\033[0;31m"
happy = """( ˶ˆᗜˆ˵ )"""

def get_logging_colour(status: str) -> str:
    
    if status == 'QUEUED':
        return yellow
    if status == 'RUNNING':
        return yellow
    if status == 'SUCCEEDED':
        return green
    if status == 'FAILED':
        return red
    if status == _:
        return red


ATHENA_QUERY_OUTPUT_PATH = "s3://aws-athena-query-results-778983355679-ca-central-1"
DATABASE = 'nbin'

def execute_athena_query(athena_client:any ,query_str:str, output_location:str = ATHENA_QUERY_OUTPUT_PATH) -> int: #time
    toc = time()
    response = athena_client.start_query_execution(
        QueryString = query_str,
        QueryExecutionContext = { 'Database': DATABASE },
        ResultConfiguration={ 'OutputLocation': output_location }
        )
    queryExecutionId = response['QueryExecutionId']
    while True:
        response: dict = athena_client.get_query_execution( QueryExecutionId = queryExecutionId)
        query_status: str = response['QueryExecution']['Status']['State']
        state_change_reason: str = response['QueryExecution']['Status'].get('StateChangeReason', '')
        now_str = datetime.datetime.now()
        now_str = now_str.strftime('%H:%M:%S')
        print(f'{query_status} {now_str}: {get_logging_colour(query_status)} {query_str[0:50]} {state_change_reason}{off}')
        if query_status == 'QUEUED':
            sleep(10)
            continue
        elif query_status == 'RUNNING':
            sleep(10)
            continue
        elif query_status == 'SUCCEEDED':
            return round(time() - toc)
        elif query_status == 'FAILED':
            if 'Table not found' in state_change_reason:
                return round(time() - toc)
            print(f'{response}\n')
            add_breadcrumb(message='athena query', data=str(query_str))
            add_breadcrumb(message='athena response', data=str(response))
            capture_exception('Failed Athena Query')
            raise Exception('AWS ERROR')
        elif query_status == 'CANCELLED':
            return
        else :
            raise NotImplementedError('unkown status {result}')

class AWSIntegration:

    def __init__(self):

        self.awsSession = None
        self.cognitoClient = None
        self.regionName = "ca-central-1"
        self.baseBucket:str = ATHENA_QUERY_OUTPUT_PATH

        self.athena_client:any = boto3.client('athena')
        self.s3Client:any = boto3.client('s3')

    def CreateSyntheticHoldingsView(self, term:str, date_str:str) -> None:
        deletion_execution_time = execute_athena_query(self.athena_client, f"DROP TABLE ftp_syntheticholdings_{term}", ATHENA_QUERY_OUTPUT_PATH)
        creation_execution_time = execute_athena_query(self.athena_client, create_ftp_syntheticholdings_relative_date_query(term, date_str), ATHENA_QUERY_OUTPUT_PATH)
        add_breadcrumb(message='CreateSyntheticHoldingsView', data={'info':[
            {'time': deletion_execution_time, 'query': f'DROP TABLE ftp_syntheticholdings_{term}'},
            {'time': creation_execution_time, 'query': create_ftp_syntheticholdings_relative_date_query(term, date_str)}
        ]}, level='info')


    def UpdateSyntheticHoldingsViews(self):

        latestDate, thisMonth, lastMonth = self.GetLatestDateAndThisMonthAndLastMonthFromS3CustodianFiles()
        print(f"Latest Date: {latestDate} \nThis Month: {thisMonth} \nLast Month: {lastMonth}")      
        self.CreateSyntheticHoldingsView("latest", latestDate)
        self.CreateSyntheticHoldingsView("currentMonth", thisMonth)
        self.CreateSyntheticHoldingsView("lastMonth", lastMonth)  


    def UpdateSyntheticHoldingsTable(self) -> None:
        deletion_execution_time = execute_athena_query(self.athena_client, f"DROP TABLE ftp_syntheticholdings")
        creation_execution_time = execute_athena_query(self.athena_client, create_ftp_syntheticholdings_query)
        add_breadcrumb(message='CreateSyntheticHoldingsView', data=[
            {'time': deletion_execution_time, 'query': f'DROP TABLE ftp_syntheticholdings'},
            {'time': creation_execution_time, 'query': create_ftp_syntheticholdings_query}
        ], level='info')

    def GetLatestDateAndThisMonthAndLastMonthFromS3CustodianFiles(self):
        """
        A stupid function that needs to be refactored AND i don't understand
        """
        try:
            s3Client = boto3.client('s3') #,aws_access_key_id=self.awsAccessKeyId, aws_secret_access_key=self.awsSecretAccessKey)
            custodianBucket = "qnext.custodian.nbin"
            filesLocation = "ftp/raw/"
            
            def ListFiles():
                """List files in specific S3 URL"""
                response = s3Client.list_objects(Bucket=custodianBucket, Prefix=filesLocation)
                for content in response.get('Contents', []):
                    currentType = "CSV" if re.search("CSV",(content.get('Key').split("/")[2])) else "CTL"
                    currentKey = re.search("[0-9].+",(content.get('Key').split("/")[2]).split(".")[0]).group() if re.search("[0-9].+",(content.get('Key').split("/")[2]).split(".")[0]) else ""
                    currentKey =  currentKey if len(currentKey) > 6 and currentKey[-2:] != "01" else currentKey[0:-2]
                    if(currentType == "CSV" and len(currentKey) > 0):
                        yield currentKey
            file_list = list(ListFiles())
            add_breadcrumb(message='fileList', data={"filelist": ", ".join(file_list)}, level='info')
            file_list.sort(reverse=True)
    
            currentYear = int("20" + file_list[0][0:2])
            currentMonth = int(file_list[0][2:4])
            currentDay = int(file_list[0][4:6])
    
            if(len(str(currentDay)) == 1):
                currentDay = "0" + str(currentDay)
            lastMonth = "-1"
            if(currentMonth != "01"):
                if(len(str(int(currentMonth) - 1)) > 1 and int(currentMonth) != 1):
                    lastMonth = str(int(currentMonth) - 1)
                else: 
                    lastMonth = ("0" + str(int(currentMonth) - 1))
            else:
                lastMonth = "12"
    
            latestDate = str(currentYear) + "-" + str(currentMonth) + "-" + str(currentDay) + "T00:00:00Z"
            thisMonth = str(currentYear) + "-" + str(lastMonth) + "-01" + "T00:00:00Z"
            lastMonth = str(currentYear) + "-" + str(lastMonth) + "-01" + "T00:00:00Z"
            return latestDate,thisMonth, lastMonth

        except Exception as e:
            print(e) 
            return

def handler(event, context):
    print(f'context: {context}. Event: {event}')

if __name__ == "__main__":
    from os import environ
    environ['SENTRY_DSN'] = "https://59aeb3cf34f043bc90c629a123fc1a6e@o1168654.ingest.sentry.io/6262116"
    handler(None, None)

