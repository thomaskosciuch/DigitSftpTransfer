from os import environ
from sentry_sdk import set_user, init, add_breadcrumb
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.utils import BadDsn

def init_sentry(turn_on: bool = True, exit_on_fail=False) -> None:
    try:
        init(
            dsn=environ['SENTRY_DSN'],
            integrations=[AwsLambdaIntegration()],
            traces_sample_rate=0.01,
            max_breadcrumbs=50,
        )
    except BadDsn:
        print('bad DSN. Sentry off.')
        if exit_on_fail:
            raise Exception('Could not start Sentry. Failing lambda.')



