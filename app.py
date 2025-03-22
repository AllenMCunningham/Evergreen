import os
import aws_cdk as cdk
from evergreen_stack import EvergreenStack

app = cdk.App()

EvergreenStack(
    app, "EvergreenStack",
    image_path="./lambda",
    secret_values={
        "repo_url": os.getenv("REPO_URL"),
        "username": os.getenv("GITHUB_USERNAME"),
        "token": os.getenv("GITHUB_TOKEN"),
        "email": os.getenv("GITHUB_EMAIL")
    },
    schedule_expression=os.getenv("LAMBDA_CRON", "cron(0 12 * * ? *)")
)

app.synth()