from os import environ

import boto3
from paramiko import SFTPAttributes
from pysftp import Connection
from constants import IDENTIFIER, SOURCE_DIRECTORY

def older_than(source_time:int , destination_time:int) -> bool:
    return source_time <= destination_time

def get_files_absent_from_dynamo(source_connection: Connection) -> list[str]:
    source_files: list[SFTPAttributes] = source_connection.listdir_attr(SOURCE_DIRECTORY)
    source_files: list[SFTPAttributes] = list(filter(lambda file: IDENTIFIER in file.filename, source_files))
    source_file_array: list[str] = [file.filename for file in source_files]
    
    
    dynamodb = boto3.client('dynamodb')
    table_name = environ['DYNAMO_TABLE_NAME']

    response = dynamodb.scan(
        TableName=table_name,
        ProjectionExpression='filename'
    )

    items: list[str] = [x['filename']['S'] for x in response['Items']]

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(
            TableName=table_name,
            ProjectionExpression='filename',
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        for item in response['Items']:
            items.append(item['filename']['S'])
    missing_entries: list[str] = [value for value in source_file_array if value not in items]
    return missing_entries
