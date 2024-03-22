from aws_cdk import (
    Duration,
    Stack,
)
from constructs import Construct
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        lambda_function = _lambda.Function(
            self, "update_notion_db",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/lambda_package.zip"),
            timeout=Duration.minutes(5),
            memory_size=256
        )

        lambda_function.add_to_role_policy(iam.PolicyStatement(
            actions=["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
            resources=["arn:aws:ssm:us-west-2:{YOUR_AWS_ACCOUNT_ID}:parameter/yt_notion_lambda/*"],
            effect=iam.Effect.ALLOW
        ))

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(Duration.hours(1)),
        )

        rule.add_target(targets.LambdaFunction(lambda_function))
