from constructs import Construct
from aws_cdk import (
    Stack,
    BundlingOptions,
    Duration,
    aws_lambda,
    aws_events,
    aws_events_targets,
    aws_iam,
)

from cdk_build.env_vars import digit_nbin_ftp_env_vars

TOPIC_ID = 'digit_upload_topic'


class Digit2NbinStack(Stack):
    """
    Moves data from DIGIT FTP to NBIN FTP 
    """

    cron_schedule: aws_events.Schedule = aws_events.Schedule.cron(
        minute='/5', hour='20', month='*', week_day='MON-FRI', year='*') #3pm in UTC

    cron_schedule_2: aws_events.Schedule = aws_events.Schedule.cron(
        minute='0', hour='12-19', month='*', week_day='MON-FRI', year='*') #9-5 in UTC


    def cron(self, aws_events, cycle, n=0) -> aws_events:
        return aws_events.Rule(
            self, f"Rule{n}",
            schedule=cycle,
        )

    def __init__(self, scope: Construct, construct_id='digitNbinTransfer', **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.name: str = construct_id

        digit_nbin_transfer = aws_lambda.Function(
            self,
            self.name,
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=aws_lambda.Code.from_asset(
                self.name,
                bundling=BundlingOptions(
                    image=aws_lambda.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output"
                    ],
                )
            ),
            timeout=Duration.minutes(10),
            environment=digit_nbin_ftp_env_vars(self),
            handler='main.handler'
        )

        policy_statement: aws_iam.PolicyStatement = aws_iam.PolicyStatement(
            # principals=[aws_iam.AnyPrincipal()],
            actions=[
                "cloudformation:*",
                "cloudwatch:DeleteAlarms",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:GetMetricData",
                "cloudwatch:PutMetricAlarm",
                'ses:SendEmail',
                'ses:SendRawEmail',
                'ses:SendTemplatedEmail',
            ],
            resources=["*"]
        )
        digit_nbin_transfer.add_to_role_policy(policy_statement)

        rule = self.cron(aws_events, self.cron_schedule, 1)
        rule.add_target(aws_events_targets.LambdaFunction(
            digit_nbin_transfer, retry_attempts=10))

        rule2 = self.cron(aws_events, self.cron_schedule_2, 2)
        rule2.add_target(aws_events_targets.LambdaFunction(
            digit_nbin_transfer, retry_attempts=10))
