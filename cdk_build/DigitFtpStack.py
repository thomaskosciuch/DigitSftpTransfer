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

    cron_schedule = aws_events.Schedule.cron(
        minute='10', hour='*', month='*', week_day='TUE-SAT', year='*')

    def cron(self, aws_events, cycle) -> aws_events:
        return aws_events.Rule(
            self, "Rule",
            schedule=cycle,
        )

    def __init__(self, scope: Construct, construct_id='d1g1t_nbin_transfer', **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.name: str = construct_id

        digit_nbin_transfer = aws_lambda.Function(
            self,
            self.name,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset(
                "sftp_transfer_lambda",
                bundling=BundlingOptions(
                    image=aws_lambda.Runtime.PYTHON_3_9.bundling_image,
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

        policy_statement = aws_iam.PolicyStatement(
            # principals=[aws_iam.AnyPrincipal()],
            actions=[
                "cloudformation:*"
                "cloudwatch:DeleteAlarms",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:GetMetricData",
                "cloudwatch:PutMetricAlarm",
            ],
            resources=["*"]
        )
        digit_nbin_transfer.add_to_role_policy(policy_statement)

        rule = self.cron(aws_events, self.cron_schedule,)
        rule.add_target(aws_events_targets.LambdaFunction(
            digit_nbin_transfer, retry_attempts=10))
