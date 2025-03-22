import json
from aws_cdk import (
    Stack,
    Duration,
    SecretValue,
    aws_ecr_assets as ecr_assets,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

class EvergreenStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, image_path: str, secret_values: dict, schedule_expression: str = "cron(0 12 * * ? *)", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Secrets Manager Secret
        secret = secretsmanager.Secret(
            self, "GitHubSecret",
            secret_name=secret_values.get("name", "github-keep-green"),
            secret_string_value=SecretValue.unsafe_plain_text(json.dumps(secret_values))
        )

        # 2. Lambda Role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"))

        # 3. Docker-based Lambda
        fn = _lambda.DockerImageFunction(
            self, "KeepGreenLambda",
            function_name="evergreen-committer",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=image_path,
                platform=ecr_assets.Platform.LINUX_AMD64),
            role=lambda_role,
            environment={
                "SECRET_NAME": secret.secret_name
            },
            timeout=Duration.seconds(30),
        )

        # 4. CloudWatch Scheduled Event
        rule = events.Rule(
            self, "ScheduledRule",
            schedule=events.Schedule.expression(schedule_expression)
        )

        rule.add_target(targets.LambdaFunction(fn))