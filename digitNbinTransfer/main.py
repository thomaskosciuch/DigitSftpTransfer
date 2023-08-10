from pysftp import Connection
from sentry_sdk import capture_exception

from compare_files import get_files_absent_from_destination
from constants import DESTINATION_DIRECTORY
from send_email import send_email, format_successful_email, format_failed_email
from sftp_connections import digit_sftp_connection, nbin_sftp_connection

#PLACEHOLDER FUNCTION
def get_length_of_file(files_to_add: list[dict]) -> int:
    #TODO get length of the contents of the files 
    return 1

#PLACEHOLDER FUNCTION
def transfer_files(files_to_add:list[dict]) -> int:
    length = 0
    # TODO
    # for file in transfer_files()...
    # get_length_of_file()
    return length

def handler(event, context):

    digit_connection: Connection = digit_sftp_connection()
    nbin_connection: Connection = nbin_sftp_connection()
    
    files_to_add: list[dict] = get_files_absent_from_destination(digit_connection, nbin_connection)

    cumulative_length_of_transferred_entries:int = 0

    try:
        success=True
        cumulative_length_of_transferred_entries = transfer_files(files_to_add)
        # i don't want to send emails yet...
    except Exception as exception:
        success=False
        print(exception)

    if success:
        message = format_successful_email(cumulative_length_of_transferred_entries, DESTINATION_DIRECTORY)
    else:
        message = format_failed_email(len(files_to_add))
        capture_exception(exception)
    send_email(message)

if __name__ == "__main__":
    handler(None, None)