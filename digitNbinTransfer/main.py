from pysftp import Connection
from sentry_sdk import capture_exception
from paramiko import SFTPClient

from compare_files import get_files_absent_from_destination
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
    for file in files_to_add:
        filepath: str = f'{SOURCE_DIRECTORY}/{file}'
        length += get_length_of_file(filepath, source)
        with source.open(filepath) as opened_file:
            destination.putfo(opened_file, f'{DESTINATION_DIRECTORY}/{file}')
    return length

def handler(event, context):

    message: SesMessage

    try:
        init_sentry()
        digit_connection: Connection = digit_sftp_connection()
        nbin_connection: Connection = nbin_sftp_connection()
        files_to_add: list[str] = get_files_absent_from_destination(digit_connection, nbin_connection)
        if len(files_to_add) == 0:
            print('no files. Exiting early.')
            exit()
        cumulative_length_of_transferred_entries:int = 0
        cumulative_length_of_transferred_entries = transfer_files(files_to_add, digit_connection.sftp_client, nbin_connection.sftp_client)
        message = format_successful_email(cumulative_length_of_transferred_entries, DESTINATION_DIRECTORY)
    except Exception as exception:
        message = format_failed_email(len(files_to_add), str(exception))
        capture_exception(exception)
    send_email(message)

if __name__ == "__main__":
    handler(None, None)