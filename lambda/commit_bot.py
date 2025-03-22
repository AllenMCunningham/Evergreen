import os
import boto3
import base64
import subprocess
import shutil
from datetime import datetime
import random

def get_secret(secret_name):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return eval(response["SecretString"])

def add_and_commit(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)


def lambda_handler(event, context):
    secret = get_secret(os.environ['SECRET_NAME'])
    repo_url = secret['repo_url']
    username = secret['username']
    email = secret['email']
    token = secret['token']

    clone_url = repo_url.replace("https://", f"https://{username}:{token}@")
    repo_name_raw = repo_url.split("/")[-1].replace(".git", "")
    repo_path = f"/tmp/{repo_name_raw}"

    # Clean up any previous repo
    shutil.rmtree(repo_path, ignore_errors=True)

    # Clone the repo into /tmp
    subprocess.run(["git", "clone", clone_url, repo_path], check=True)
    os.chdir(repo_path)

    subprocess.run(["git", "config", "user.name", username], check=True)
    subprocess.run(["git", "config", "user.email", email], check=True)
    for x in range(random.randint(1, 45)):
        # Create a meaningless commit
        filename = f"keepgreen_{datetime.utcnow().isoformat()}.txt"
        with open(filename, "w") as f:
            f.write("Staying green")

        add_and_commit("chore: keep green")
        # delete said file after commit and push
        os.remove(filename)
        add_and_commit("chore: remove keepgreen file")
    subprocess.run(["git", "push"], check=True)
    return {"status": "Committed"}