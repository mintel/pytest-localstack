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
SERVICE_PORTS = {
    "apigateway": 4567,
    "cloudformation": 4581,
    "cloudwatch": 4582,
    "dynamodb": 4569,
    "dynamodbstreams": 4570,
    "es": 4578,
    "firehose": 4573,
    "kinesis": 4568,
    "lambda": 4574,
    "redshift": 4577,
    "route53": 4580,
    "s3": 4572,
    "ses": 4579,
    "sns": 4575,
    "ssm": 4583,
    "sqs": 4576,
}

# AWS uses multiple names for some services. Map alias to service name.
SERVICE_ALIASES = {
    "monitoring": "cloudwatch",
    "email": "ses",
    "streams.dynamodb": "dynamodbstreams",
}

DEFAULT_CONTAINER_START_TIMEOUT = 60
DEFAULT_CONTAINER_STOP_TIMEOUT = 10

BOTOCORE_VERSION = get_version_tuple(botocore.__version__)
