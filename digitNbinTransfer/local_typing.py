from typing import Required, NotRequired, LiteralString, TypedDict

class DigitCredentials(TypedDict):
    digit_sftp_passphrase: Required[str]
    digit_sftp_ppk: Required[str]
    digit_sftp_server: Required[str]
    digit_sftp_username: Required[str]
    email_maintainer: Required[list[str]]
    email_recipient: NotRequired[list[str]]
    email_reply_address: Required[str]
    email_sender: Required[str]
    name: Required[str]
    nbin_sftp_password: Required[str]
    nbin_sftp_username: Required[str]
    sentry_dsn: Required[str]

class SesContentBlock(TypedDict):
    Body: str
    Charset: LiteralString #'UFT-8'

class SesBodyBlock(TypedDict):
    Body: SesContentBlock
    Html: SesContentBlock

class SesMessage(TypedDict):
    Subject: SesContentBlock
    Body: SesContentBlock

