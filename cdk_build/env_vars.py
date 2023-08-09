from typing import TypedDict, LiteralString, Required
from aws_cdk import aws_ssm

class DigitCredentials(TypedDict):
    digit_sftp_ppk: Required[str]
    digit_sftp_server: Required[str]
    digit_sftp_private_key_pass: Required[str]
    digit_sftp_username: Required[str]
    name: Required[str]
    nbin_sftp_password: Required[str]
    nbin_sftp_username: Required[str]
    sentry_dsn: Required[str]

DIGIT_FTP_SERVER:LiteralString = 'ca.sftp.d1g1t.com'
NBIN_FTP_SERVER:LiteralString = 'sftp.corrnet.com'

def digit_nbin_ftp_env_vars(self) -> DigitCredentials:
    get_ssm_value = aws_ssm.StringParameter.value_for_string_parameter
    
    digit_sftp_ppk = get_ssm_value(self, "DIGIT_FTP_PPK")
    digit_sftp_private_key_pass = get_ssm_value(self, "DIGIT_SFTP_PRIVATE_KEY_PASS")
    digit_sftp_username = get_ssm_value(self, 'DIGIT_SFTP_USERNAME')
    nbin_sftp_password = get_ssm_value(self, "SFTP_NBIN_PASSWORD")
    nbin_sftp_username = get_ssm_value(self, "SFTP_NBIN_USERNAME")
    sentry_dsn = get_ssm_value(self, "LAMBDA_SENTRY_DSN")
    
    return {
        "digit_sftp_ppk": digit_sftp_ppk,
        "digit_sftp_server": DIGIT_FTP_SERVER,
        "digit_sftp_private_key_pass": digit_sftp_private_key_pass, 
        "digit_sftp_username": digit_sftp_username,
        "name": self.name,
        "nbin_sftp_password": nbin_sftp_password,
        "nbin_sftp_server": NBIN_FTP_SERVER,
        "nbin_sftp_username": nbin_sftp_username,
        "sentry_dsn": sentry_dsn
    }
