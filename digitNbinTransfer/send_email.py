from datetime import datetime
from io import TextIOWrapper
from os import getenv, environ

from boto3 import client
from pytz import timezone

from local_typing import SesMessage
from constants import DESTINATION_DIRECTORY_VISIBLE, DEFAULT_EMAIL_MAINTAINER, \
      DEFAULT_EMAIL_RECIPIENT, DEFAULT_EMAIL_REPLY_ADDRESS

local_datetime = datetime.now(timezone('America/Toronto'))

def format_successful_email(n_transactions: int, destination:str) -> SesMessage:
        SUCCESS_STR: str = """{n_transactions} were successfully sent to NBIN’s FTP folder at {time} on {date}. A copy of the file can be found in {destination}."""

        html_raw: TextIOWrapper = open('success_email.html', 'r')
        html_str: str = ""
        for line in html_raw.readlines():
            html_str += line
        html_str = html_str.replace('{n_transactions}', str(n_transactions)).\
            replace('{time}', local_datetime.strftime('%H:%M:%S')).\
            replace('{date}', local_datetime.strftime('%B %d, %Y')).\
            replace('{destination}', destination)
        
        str_str = SUCCESS_STR.replace('{n_transactions}', str(n_transactions)).\
            replace('{time}', local_datetime.strftime('%H:%M:%S')).\
            replace('{date}', local_datetime.strftime('%B %d, %Y')).\
            replace('{destination}', destination)

        message: SesMessage = {
            'Subject': {'Data': 'SUCCESSFUL d1g1t nbin SFTP transfer', 'Charset':'UTF-8'},
            'Body': {
                "Text": {'Data': str_str, 'Charset':'UTF-8'},
                'Html': {'Data': html_str, 'Charset':'UTF-8'}
            }
        }
        return message

def format_failed_email(x_files: int, exception_str: str) -> SesMessage:
        FAILED_STR: str = """{x_files} transactions files failed to upload to NBIN’s FTP folder at {time} on {date}."""

        html_raw: TextIOWrapper = open('failed_email.html', 'r')
        html_str: str = ""
        for line in html_raw.readlines():
            html_str += line
        html_str = html_str.replace('{x_files}', str(x_files)).\
            replace('{time}', local_datetime.strftime('%H:%M:%S')).\
            replace('{date}', local_datetime.strftime('%B %d, %Y')).\
            replace('{ERROR_STRING}', exception_str).\
            replace('{source}', DESTINATION_DIRECTORY_VISIBLE)

        _str = FAILED_STR.replace('{x_files}', str(x_files)).\
            replace('{time}', local_datetime.strftime('%H:%M:%S')).\
            replace('{date}', local_datetime.strftime('%B %d, %Y')).\
            replace('{source}', DESTINATION_DIRECTORY_VISIBLE)
        message: SesMessage = {
            'Subject': {'Data': 'FAILED d1g1t nbin SFTP transfer', 'Charset':'UTF-8'},
            'Body': {
                "Text": {'Data':_str, 'Charset':'UTF-8'},
                'Html': {'Data': html_str, 'Charset':'UTF-8'}
            }
        }
        return message

def send_email(message: SesMessage, bcc_maintainer=False) -> None:
    ses_client = client('ses') #botocore.Client.Base ; but useless type
    ses_client.send_email(
        Source=environ['email_sender'],
        Destination={
            'ToAddresses': [getenv('email_recipient', DEFAULT_EMAIL_RECIPIENT)],
            'CcAddresses': [],
            'BccAddresses': [getenv('email_maintainer', DEFAULT_EMAIL_MAINTAINER)] if bcc_maintainer else []
        },
        ReplyToAddresses=[getenv('email_reply_address', DEFAULT_EMAIL_REPLY_ADDRESS)],
        Message=message,
        SourceArn='arn:aws:ses:ca-central-1:778983355679:identity/welcome@qwealth.com',
    )
