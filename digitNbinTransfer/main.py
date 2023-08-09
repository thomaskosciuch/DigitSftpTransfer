from os import environ
from typing import TypedDict, Required, LiteralString
from io import StringIO

from paramiko import SFTPAttributes, RSAKey
from pysftp import Connection, CnOpts

class DigitCredentials(TypedDict):
    digit_sftp_ppk: Required[str]
    digit_sftp_server: Required[str]
    digit_sftp_passphrase: Required[str]
    digit_sftp_username: Required[str]
    name: Required[str]
    nbin_sftp_password: Required[str]
    nbin_sftp_username: Required[str]
    sentry_dsn: Required[str]

SOURCE_DIRECTORY: LiteralString = '/trade-orders/mf-trades'
DESTINATION_DIRECTORY: LiteralString = ''

def nbin_sftp_connection() -> Connection:
    cnopts = CnOpts()
    cnopts.hostkeys = None
    conn_params = {
        'host': environ['nbin_sftp_server'],
        'username': environ['nbin_sftp_username'],
        'cnopts': cnopts,
        'password': environ['nbin_sftp_password']
    }
    conn = Connection(**conn_params)
    return conn

def digit_sftp_connection() -> Connection:
    cnopts = CnOpts()
    cnopts.hostkeys = None
    private_key= RSAKey.from_private_key(StringIO(environ['digit_sftp_ppk']), password=environ['digit_sftp_private_key_pass'])
    conn_params = {
        'host': environ['digit_sftp_server'],
        'username': environ['digit_sftp_username'],
        'cnopts': cnopts,
        'private_key': private_key
        
    }
    conn = Connection(**conn_params)
    return conn

def handler(event, context):

    IDENTIFIER: LiteralString = 'dmfQWEA'


    digit_connection: Connection = digit_sftp_connection()
    source_files: list[SFTPAttributes] = digit_connection.listdir_attr(SOURCE_DIRECTORY)
    source_files: list[SFTPAttributes] = list(filter(lambda file: IDENTIFIER in file.filename, source_files))
    source_file_array: list[str] = [file.filename for file in source_files]
    source_file_times: dict[str, int] = {file.filename: file.st_mtime for file in source_files}
    
    nbin_connection: Connection = nbin_sftp_connection()
    destination_files: list[SFTPAttributes] = nbin_connection.listdir_attr()
    destination_files: list[SFTPAttributes] = list(filter(lambda file: file.filename in source_file_array, destination_files))
    destination_file_times: dict[str, int] = {file.filename: file.st_mtime for file in destination_files}

    files_to_add: list[str] = []
    
    def older_than(source_time:int , destination_time:int) -> bool:
        return source_time <= destination_time

    for source_file, source_time in source_file_times.items():
        if source_file in destination_file_times:
            if older_than(source_time, destination_file_times[source_time]):
                continue
            files_to_add.append(source_file)
        else:
            files_to_add.append(source_file)

    for file in files_to_add:
        print(f'ADD FILE: {file}')
    


if __name__ == "__main__":
    handler(None, None)