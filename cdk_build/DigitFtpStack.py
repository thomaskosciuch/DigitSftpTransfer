from constructs import Construct
from aws_cdk import (
    Stack,
    BundlingOptions,
    Duration,
    aws_lambda,
    aws_events,
    aws_events_targets,
    aws_iam,
    aws_ses_actions
)

from cdk_build.env_vars import digit_nbin_ftp_env_vars

TOPIC_ID = 'digit_upload_topic'


class Digit2NbinStack(Stack):
    """
    Moves data from DIGIT FTP to NBIN FTP 
    """

    cron_schedule: aws_events.Schedule = aws_events.Schedule.cron(
        minute='10', hour='*', month='*', week_day='*', year='*')

    def cron(self, aws_events, cycle) -> aws_events:
        return aws_events.Rule(
            self, "Rule",
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

        policy_statement = aws_iam.PolicyStatement(
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

        rule = self.cron(aws_events, self.cron_schedule,)
        rule.add_target(aws_events_targets.LambdaFunction(
            digit_nbin_transfer, retry_attempts=10))

    # topic = sns.Topic(self, "Topic")

    # ses.ReceiptRuleSet(self, "RuleSet",
    #     rules=[ses.ReceiptRuleOptions(
    #         recipients=["hello@aws.com"],
    #         actions=[
    #             actions.AddHeader(
    #                 name="X-Special-Header",
    #                 value="aws"
    #             ),
    #             actions.S3(
    #                 bucket=bucket,
    #                 object_key_prefix="emails/",
    #                 topic=topic
    #             )
    #         ]
    #     ), ses.ReceiptRuleOptions(
    #         recipients=["aws.com"],
    #         actions=[
    #             actions.Sns(
    #                 topic=topic
    #             )
    #         ]
    #     )
    #     ]
    # )

    # TODO integrate SES