import aws_cdk
# from cdk_build.DigitFtpStack import Digit2NbinStack
from cdk_build.CronjobThing import CronjobThing
app = aws_cdk.App()
CronjobThing(app)
# Digit2NbinStack(app)
app.synth()