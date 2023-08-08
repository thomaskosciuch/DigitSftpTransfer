import aws_cdk
from cdk_build.DigitFtpStack import Digit2NbinStack
app = aws_cdk.App()
Digit2NbinStack(app, "sftp-2-s3-upload-stack")
app.synth()