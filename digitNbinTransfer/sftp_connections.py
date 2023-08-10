
from os import environ
from io import StringIO

from paramiko import RSAKey
from pysftp import Connection, CnOpts

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
