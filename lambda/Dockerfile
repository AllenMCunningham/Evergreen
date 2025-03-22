FROM public.ecr.aws/lambda/python:3.10

# Install git
RUN yum install -y git && yum clean all

COPY requirements.txt ./
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy function code
COPY commit_bot.py ./

# Set the CMD to your handler
CMD ["commit_bot.lambda_handler"]