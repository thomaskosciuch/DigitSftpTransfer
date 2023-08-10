# DigitSftpTransfer
Trade requests files are generated from d1g1t every hour until 2pm, and then every 30 minutes, 10 minutes and 5 minutes leading up to 4pm. This will check which files in the source (d1g1t) are newer than or don't exist in the destination (NBIN) and transfer them.

Any uploaded files will be opened and the quantity of rows, which correspond to transactions are counted and digested in an email.

If no files are uploaded, then no files are transfered. No emails are sent.

If for any reason we encounter a failure, an email is sent to the distribution list and recorded in our [error reporting software](https://qwealth.sentry.io/issues/?project=6262116)


# How it works
We executing a cron-job using [eventbridge](https://aws.amazon.com/eventbridge/) that triggers a [lambda](https://aws.amazon.com/lambda/) function and moves files from A to B using ssh file transfer protocols ([SFTP](https://en.wikipedia.org/wiki/SSH_File_Transfer_Protocol)).

## SFTP
The lambda is using [pysftp](https://docs.paramiko.org/en/latest/api/sftp.html#paramiko.sftp_client.SFTPClient.open) to create a connection, then I use the exposed the underlying [paramiko](https://docs.paramiko.org/en/latest/index.html) client (able to conduct more advanced operations) to read, and transfer the file.

## Emails
If the SFTP file transfer fails or succeeds emails are sent using [SES](https://aws.amazon.com/ses/)

# Issues
- Currently we are using welcome@qwealth.com instead of a not-stupid email
- Currently I have made the cron-job run every 10 minutes instead of the pattern suggested
- Currently the error reporting is lacklustre

# How to maintain:
Write code here. `cdk deploy` will use run app.py, which then builds the what exists in `cdk_build/DigitFtpStack` [sic]. 
Note that the cdk.out file contains assets each time that this is deployed, and therefore should manually be deleted every now and then.