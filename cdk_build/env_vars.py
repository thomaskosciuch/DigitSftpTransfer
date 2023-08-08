from typing import TypedDict, LiteralString, Required
from aws_cdk import aws_ssm


class DigitCredentials(TypedDict):
    digit_ftp_ppk: Required[str]
    digit_ftp_server: Required[str]
    name: Required[str]
    nbin_ftp_password: Required[str]
    nbin_ftp_username: Required[str]
    sentry_dsn: Required[str]

DIGIT_FTP_SERVER:LiteralString = 'ca.sftp.d1g1t.com'
NBIN_FTP_SERVER = 'sftp.corrnet.com'

def digit_nbin_ftp_env_vars(self) -> DigitCredentials:
    get_ssm_value = aws_ssm.StringParameter.value_for_string_parameter
    
    digit_ftp_ppk = get_ssm_value(self, "DIGIT_FTP_PPK")
    nbin_ftp_password = get_ssm_value(self, "NBIN_FTP_PASSWORD")
    nbin_ftp_username = get_ssm_value(self, "NBIN_FTP_USERNAME")
    sentry_dsn = get_ssm_value(self, "LAMBDA_SENTRY_DSN")
    
    return {
        "digit_ftp_ppk": digit_ftp_ppk,
        "digit_ftp_server": DIGIT_FTP_SERVER,
        "name": self.name,
        "nbin_ftp_password": nbin_ftp_password,
        "nbin_ftp_username": nbin_ftp_username,
        "sentry_dsn": sentry_dsn
    }
