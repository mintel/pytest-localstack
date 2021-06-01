"""Checks to see if Localstack service is running.

Each check takes a :class:`.LocalstackSession` and
raises :class:`~pytest_localstack.exceptions.ServiceError`
if the service is not available.
"""
import contextlib
import functools
import socket
import urllib.parse

import botocore.config

from pytest_localstack import constants, exceptions


def is_port_open(port_or_url, timeout=1):
    """Check if TCP port is open."""
    if isinstance(port_or_url, (str, bytes)):
        url = urllib.parse.urlparse(port_or_url)
        port = url.port
        host = url.hostname
    else:
        port = port_or_url
        host = "127.0.0.1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with contextlib.closing(sock):
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        return result == 0


def port_check(service_name):
    """Check that a service port is open."""

    def _check(localstack_session):
        url = localstack_session.endpoint_url(service_name)
        if not is_port_open(url):
            raise exceptions.ServiceError(service_name=service_name)

    return _check


def botocore_check(service_name, client_func_name):
    """Decorator to check service via botocore Client.

    `client_func_name` should be the name of a harmless client
    method to call that has no required arguements.
    `list_*` methods are usually good candidates.
    """

    def _decorator(check_results_func):
        @functools.wraps(check_results_func)
        def _wrapped(localstack_session):
            url = localstack_session.endpoint_url(service_name)
            if not is_port_open(url):
                raise exceptions.ServiceError(service_name=service_name)
            config_kwargs = {
                "connect_timeout": 1,
                "read_timeout": 1,
                "s3": {"addressing_style": "path"},
            }
            if constants.BOTOCORE_VERSION >= (1, 6, 0):
                config_kwargs["retries"] = {"max_attempts": 1}
            client = localstack_session.botocore.client(
                service_name,
                # Handle retries at a higher level
                config=botocore.config.Config(**config_kwargs),
            )
            client_func = getattr(client, client_func_name)
            try:
                response = client_func()
                check_results_func(response)
            except Exception as e:
                raise exceptions.ServiceError(service_name=service_name) from e

        return _wrapped

    return _decorator


def botocore_check_response_type(
    service_name, client_func_name, expected_type, *response_keys
):
    """Generate a service check function that tests that the response is a specific type.

    Optionally pass response_keys to check the type of something nested in a
    response dict.
    """

    @botocore_check(service_name, client_func_name)
    def _f(client_response):
        for key in response_keys:
            client_response = client_response[key]
        if not isinstance(client_response, expected_type):
            raise TypeError(
                f"Client response type {client_response.__class__.__name__} is not a subtype of {expected_type.__name__}"
            )

    return _f


SERVICE_CHECKS = {
    "events": port_check("events"),
    "apigateway": port_check(
        "apigateway"  # moto doesn't implement a good apigateway endpoint for checks yet.
    ),
    "cloudformation": botocore_check_response_type(
        "cloudformation", "list_stacks", list, "StackSummaries"
    ),
    "cloudwatch": botocore_check_response_type(
        "cloudwatch", "list_dashboards", list, "DashboardEntries"
    ),
    "dynamodb": botocore_check_response_type(
        "dynamodb", "list_tables", list, "TableNames"
    ),
    "dynamodbstreams": botocore_check_response_type(
        "dynamodbstreams", "list_streams", list, "Streams"
    ),
    "ec2": botocore_check_response_type("ec2", "describe_regions", list, "Regions"),
    "es": botocore_check_response_type("es", "list_domain_names", list, "DomainNames"),
    "firehose": botocore_check_response_type(
        "firehose", "list_delivery_streams", list, "DeliveryStreamNames"
    ),
    "iam": botocore_check_response_type("iam", "list_roles", list, "Roles"),
    "kinesis": botocore_check_response_type(
        "kinesis", "list_streams", list, "StreamNames"
    ),
    "lambda": botocore_check_response_type(
        "lambda", "list_functions", list, "Functions"
    ),
    "logs": botocore_check_response_type(
        "logs", "describe_log_groups", list, "logGroups"
    ),
    "redshift": botocore_check_response_type(
        "redshift", "describe_clusters", list, "Clusters"
    ),
    "route53": port_check(
        "route53"  # moto doesn't implement a good route53 endpoint for checks yet.
    ),
    "s3": botocore_check_response_type("s3", "list_buckets", list, "Buckets"),
    "secretsmanager": botocore_check_response_type(
        "secretsmanager", "list_secrets", list, "SecretList"
    ),
    "ses": botocore_check_response_type("ses", "list_identities", list, "Identities"),
    "sns": botocore_check_response_type("sns", "list_topics", list, "Topics"),
    "sqs": botocore_check_response_type(
        "sqs", "list_queues", dict  # https://github.com/boto/boto3/issues/1813
    ),
    "ssm": botocore_check_response_type(
        "ssm", "describe_parameters", list, "Parameters"
    ),
    "stepfunctions": botocore_check_response_type(
        "stepfunctions", "list_activities", list, "activities"
    ),
    "sts": port_check(
        "sts"  # moto doesn't implement a good sts endpoint for checks yet.
    ),
}

# All services should have a check.
assert set(SERVICE_CHECKS) == set(constants.SERVICE_PORTS)  # nosec
