from os import environ
import boto3
import sys
import traceback
import uuid
from datetime import datetime

from pysftp import Connection
from sentry_sdk import capture_exception, add_breadcrumb, capture_message
from paramiko import SFTPClient

from compare_files import get_files_absent_from_dynamo
from local_typing import SesMessage
from constants import DESTINATION_DIRECTORY, SOURCE_DIRECTORY
from send_email import send_email, format_successful_email, format_failed_email
from sftp_connections import digit_sftp_connection, nbin_sftp_connection
from sentry import init_sentry


def get_length_of_file(filepath: str, source:SFTPClient) -> int:
    with source.open(filepath) as opened_file:
        return len(opened_file.readlines()) - 1

def transfer_files(files_to_add:list[dict], source: SFTPClient, destination: SFTPClient) -> int:
    length:int=0
    dynamodb = boto3.client('dynamodb')
    for file in files_to_add:
        print(f'file to add {file}')
        filename = file
        filepath: str = f'{SOURCE_DIRECTORY}/{file}'
        length += get_length_of_file(filepath, source)
        with source.open(filepath) as opened_file:
            destination.putfo(opened_file, f'{DESTINATION_DIRECTORY}/{file}')
        with source.open(filepath) as opened_file:
            timestamp = datetime.utcnow().isoformat()
            item = {
                'id': {'S': str(uuid.uuid4())},
                'filename': {'S': filename},
                'contents': {'B': opened_file.read()},
                'timestamp': {'S': timestamp}
            }
            response = dynamodb.put_item(TableName=environ['DYNAMO_TABLE_NAME'], Item=item)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                capture_message(message=f'Could not add {file} to dynamo.', level='warning')
                print(f'could not add {file} to dynamo')
    return length

def handler(event, context):

    message: SesMessage
    files_to_add: list[str] = []
    try:
        init_sentry()
        digit_connection: Connection = digit_sftp_connection()
        nbin_connection: Connection = nbin_sftp_connection()
        files_to_add = get_files_absent_from_dynamo(digit_connection)
        if len(files_to_add) == 0:
            print('no files. Exiting early.')
            return
        cumulative_length_of_transferred_entries:int = 0
        cumulative_length_of_transferred_entries = transfer_files(files_to_add, digit_connection.sftp_client, nbin_connection.sftp_client)
        add_breadcrumb(message='files', category='logging', data = {
            'n_files': len(files_to_add), 'n_transactions': cumulative_length_of_transferred_entries, 'files': files_to_add
            })
        message = format_successful_email(cumulative_length_of_transferred_entries, DESTINATION_DIRECTORY)
        send_email(message)
        capture_message(message='D1G1T NBIN TRANSFER', level='info')
        print(f'done n_files: {len(files_to_add)}')
    except Exception as exception:
        traceback_capture:str = str(exception)
        traceback_capture += '\n\n'
        traceback_capture += traceback.format_exc()
        traceback_capture += str(sys.exc_info()[2])
        traceback_capture = traceback_capture.replace('\n','<br>')

        message = format_failed_email(len(files_to_add), traceback_capture)
        capture_exception(exception)
        send_email(message, bcc_maintainer=True)

if __name__ == "__main__":
    handler(None, None)