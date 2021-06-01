"""pytest-localstack constants."""

import botocore

from pytest_localstack import utils


# IP for localhost
LOCALHOST = "127.0.0.1"

# The default AWS region.
DEFAULT_AWS_REGION = "us-east-1"

# The default AWS access key.
DEFAULT_AWS_ACCESS_KEY_ID = "accesskey"  # nosec

# The default AWS secret access key.
DEFAULT_AWS_SECRET_ACCESS_KEY = "secretkey"  # nosec

# The default AWS session token.
DEFAULT_AWS_SESSION_TOKEN = "token"  # nosec

# Mapping AWS service name to default Localstack port.
LEGACY_SERVICE_PORTS = {
    "apigateway": 4567,
    "cloudformation": 4581,
    "cloudwatch": 4582,
    "dynamodb": 4569,
    "dynamodbstreams": 4570,
    "ec2": 4597,
    "es": 4578,
    "events": 4587,
    "firehose": 4573,
    "iam": 4593,
    "kinesis": 4568,
    "lambda": 4574,
    "logs": 4586,
    "redshift": 4577,
    "route53": 4580,
    "s3": 4572,
    "secretsmanager": 4584,
    "ses": 4579,
    "sns": 4575,
    "sqs": 4576,
    "ssm": 4583,
    "stepfunctions": 4585,
    "sts": 4592,
}

SERVICE_PORTS = {k: 4566 for k in LEGACY_SERVICE_PORTS}

# AWS uses multiple names for some services. Map alias to service name.
SERVICE_ALIASES = {
    "email": "ses",
    "monitoring": "cloudwatch",
    "states": "stepfunctions",
    "streams.dynamodb": "dynamodbstreams",
}

DEFAULT_CONTAINER_START_TIMEOUT = 60
DEFAULT_CONTAINER_STOP_TIMEOUT = 10

BOTOCORE_VERSION = utils.get_version_tuple(botocore.__version__)
