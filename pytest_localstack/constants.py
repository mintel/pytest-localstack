"""pytest-localstack constants."""

from distutils.version import LooseVersion

import botocore


def get_version_tuple(version):
    """
    Return a tuple of version numbers (e.g. (1, 2, 3)) from the version
    string (e.g. '1.2.3').


    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    """
    loose_version = LooseVersion(version)
    version_numbers = []
    for item in loose_version.version:
        if not isinstance(item, int):
            break
        version_numbers.append(item)
    return tuple(version_numbers)


# IP for localhost
LOCALHOST = "127.0.0.1"

# The default AWS region.
DEFAULT_AWS_REGION = "us-east-1"

# The default AWS access key.
DEFAULT_AWS_ACCESS_KEY_ID = "accesskey"

# The default AWS secret access key.
DEFAULT_AWS_SECRET_ACCESS_KEY = "secretkey"

# The default AWS session token.
DEFAULT_AWS_SESSION_TOKEN = "token"

# Mapping AWS service name to default Localstack port.

SUPPORTED_SERVICES = [
    "apigateway",
    "cloudformation",
    "cloudwatch",
    "dynamodb",
    "dynamodbstreams",
    "ec2",
    "es",
    "firehose",
    "iam",
    "kinesis",
    "lambda",
    "logs",
    "redshift",
    "route53",
    "s3",
    "secretsmanager",
    "ses",
    "sns",
    "sqs",
    "ssm",
    "stepfunctions",
    "sts",
]

SERVICE_PORTS = {service:4566 for service in SUPPORTED_SERVICES}

# AWS uses multiple names for some services. Map alias to service name.
SERVICE_ALIASES = {
    "email": "ses",
    "monitoring": "cloudwatch",
    "states": "stepfunctions",
    "streams.dynamodb": "dynamodbstreams",
}

DEFAULT_CONTAINER_START_TIMEOUT = 60
DEFAULT_CONTAINER_STOP_TIMEOUT = 10

BOTOCORE_VERSION = get_version_tuple(botocore.__version__)
