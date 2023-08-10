import aws_cdk
from cdk_build.DigitFtpStack import Digit2NbinStack
# from cdk_build.SimpleEmailServiceStack import Digit2NbinEmailStack
app = aws_cdk.App()
Digit2NbinStack(app)
# Digit2NbinEmailStack(app)
app.synth()