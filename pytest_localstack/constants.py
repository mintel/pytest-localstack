"""pytest-localstack constants."""

# The default AWS region.
DEFAULT_AWS_REGION = 'us-east-1'

# The default AWS access key.
DEFAULT_AWS_ACCESS_KEY_ID = 'accesskey'

# The default AWS secret access key.
DEFAULT_AWS_SECRET_ACCESS_KEY = 'secretkey'

# The default AWS session token.
DEFAULT_AWS_SESSION_TOKEN = 'token'

# Mapping AWS service name to default Localstack port.
SERVICE_PORTS = {
    'apigateway': 4567,
    'cloudformation': 4581,
    'cloudwatch': 4582,
    'dynamodb': 4569,
    'dynamodbstreams': 4570,
    'es': 4578,
    'firehose': 4573,
    'kinesis': 4568,
    'lambda': 4574,
    'redshift': 4577,
    'route53': 4580,
    's3': 4572,
    'ses': 4579,
    'sns': 4575,
    'ssm': 4583,
    'sqs': 4576,
}

# AWS uses multiple names for some services. Map alias to service name.
SERVICE_ALIASES = {
    'monitoring': 'cloudwatch',
    'email': 'ses',
    'streams.dynamodb': 'dynamodbstreams',
}

DEFAULT_CONTAINER_START_TIMEOUT = 60
DEFAULT_CONTAINER_STOP_TIMEOUT = 10
