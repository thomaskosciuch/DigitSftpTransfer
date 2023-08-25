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

TOPIC_ID = 'digit_upload_topic'


class CronjobThing(Stack):
    """
    rushed cron fix
    """

    cron_schedule: aws_events.Schedule = aws_events.Schedule.cron(
        minute='/15', hour='*', month='*', week_day='*', year='*')


    def cron(self, aws_events, cycle, n=0) -> aws_events:
        return aws_events.Rule(
            self, f"Rule{n}",
            schedule=cycle,
        )

    def __init__(self, scope: Construct, construct_id='CronjobThing', **kwargs) -> None:
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
            timeout=Duration.minutes(1),
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
            ],
            resources=["*"]
        )
        digit_nbin_transfer.add_to_role_policy(policy_statement)

        rule = self.cron(aws_events, self.cron_schedule, 1)
        rule.add_target(aws_events_targets.LambdaFunction(
            digit_nbin_transfer, retry_attempts=10))

