"""Checks to see if Localstack service is running.

Each check takes a :class:`.LocalstackSession` and
raises :class:`~pytest_localstack.exceptions.ServiceError`
if the service is not available.
"""
from __future__ import absolute_import

import contextlib
import functools
import socket

import botocore.config
import six

from pytest_localstack import constants, exceptions


def is_port_open(port_or_url, timeout=1):
    """Check if TCP port is open."""
    if isinstance(port_or_url, six.string_types):
        url = six.moves.urllib.parse.urlparse(port_or_url)
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


def botocore_check(service_name, list_func_name):
    """Decorator to check service via botocore Client."""

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
            list_func = getattr(client, list_func_name)
            try:
                response = list_func()
                check_results_func(response)
            except Exception:
                raise exceptions.ServiceError(service_name=service_name)

        return _wrapped

    return _decorator


@botocore_check("dynamodb", "list_tables")
def check_dynamodb(client_response):
    """Check that DynamoDB is running."""
    assert isinstance(client_response["TableNames"], list)


@botocore_check("dynamodbstreams", "list_streams")
def check_dynamodb_streams(client_response):
    """Check that DynamoDB Streams is running."""
    assert isinstance(client_response["Streams"], list)


@botocore_check("s3", "list_buckets")
def check_s3(client_response):
    """Check that S3 is running."""
    assert isinstance(client_response["Buckets"], list)


@botocore_check("firehose", "list_delivery_streams")
def check_firehose(client_response):
    """Check that Firehose is running."""
    assert isinstance(client_response["DeliveryStreamNames"], list)


@botocore_check("kinesis", "list_streams")
def check_kinesis(client_response):
    """Check that Kinesis is running."""
    assert isinstance(client_response["StreamNames"], list)


@botocore_check("es", "list_domain_names")
def check_elasticsearch(client_response):
    """Check that Elasticsearch Service is running."""
    assert isinstance(client_response["DomainNames"], list)


@botocore_check("ssm", "describe_parameters")
def check_ssm(client_response):
    """Check that Simple Systems Manager Service is running."""
    assert isinstance(client_response["Parameters"], list)


SERVICE_CHECKS = {
    "apigateway": port_check("apigateway"),
    "cloudformation": port_check("cloudformation"),
    "cloudwatch": port_check("cloudwatch"),
    "dynamodb": check_dynamodb,
    "dynamodbstreams": check_dynamodb_streams,
    "es": check_elasticsearch,
    "firehose": check_firehose,
    "kinesis": check_kinesis,
    "lambda": port_check("lambda"),
    "redshift": port_check("redshift"),
    "route53": port_check("route53"),
    "s3": check_s3,
    "ses": port_check("ses"),
    "sns": port_check("sns"),
    "ssm": check_ssm,
    "sqs": port_check("sqs"),
}

# All services should have a check.
assert set(SERVICE_CHECKS) == set(constants.SERVICE_PORTS)
