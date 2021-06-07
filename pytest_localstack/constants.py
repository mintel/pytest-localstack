"""pytest-localstack constants."""

# The container port Localstack accepts traffic on.
EDGE_PORT = 4566

# The container port the Elasticsearch service runs on.
ELASTICSEARCH_PORT = 4571

# A Localstack container port that exposes debugpy if DEVELOP=true.
# https://github.com/microsoft/debugpy
DEVELOP_PORT = 5678

# The container port the Localstack web UI is exposed at.
WEB_UI_PORT = 8080

# The default AWS region.
DEFAULT_AWS_REGION = "us-east-1"

# The default AWS access key.
DEFAULT_AWS_ACCESS_KEY_ID = "accesskey"  # nosec

# The default AWS secret access key.
DEFAULT_AWS_SECRET_ACCESS_KEY = "secretkey"  # nosec

# The default AWS session token.
DEFAULT_AWS_SESSION_TOKEN = "token"  # nosec

# The default Localstack Docker image to run.
DEFAULT_IMAGE = "localstack/localstack:latest"

# AWS uses multiple names for some services. Map alias to service name.
SERVICE_ALIASES = {
    "email": "ses",
    "monitoring": "cloudwatch",
    "states": "stepfunctions",
    "streams.dynamodb": "dynamodbstreams",
}
