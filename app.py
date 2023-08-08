import aws_cdk
from cdk_build.DigitFtpStack import Digit2NbinStack
app = aws_cdk.App()
Digit2NbinStack(app)
app.synth()