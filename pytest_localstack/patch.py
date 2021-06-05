import contextlib
import functools
import logging
from typing import Union
from unittest import mock

import botocore.endpoint
import botocore.session

from pytest_localstack import constants


LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def aws_clients(endpoint_url: str, verify: Union[bool, str] = False):
    """
    A context manager function that will patch all botocore clients
    created after the patch is applied (and consequently boto3 clients)
    to always use the given endpoint URL.

    A patch will also be applied to botocore to raise an exception if it
    attempts to send any requests to AWS instead of endpoint_url.

    Args:
        endpoint_url (string): The URL that AWS clients should send requests to.
        verify (bool, str): Whether or not to verify SSL certificates.
            Defaults to False, which is not to verify.
            Can also be set to a path toa CA cert bundle file to use
            rather than the one botocore uses by default.
            Both options are useful when running Localstack with
            USE_SSL=true. This can be overridden on a per-client basis.

    Example:

      import boto3
      from pytest_localstack import patch
      with patch.aws_clients("http://localstack:4566"):
          s3 = boto3.client("s3")  # <- This will send requests to http://localstack:4566.

    """
    original_create_client = botocore.session.Session.create_client

    @functools.wraps(original_create_client)
    def create_client(self, *args, **kwargs):
        optional_kwargs = {
            "verify": verify,
        }
        required_kwargs = {
            "endpoint_url": endpoint_url,
        }
        kwargs = {**optional_kwargs, **kwargs, **required_kwargs}
        return original_create_client(self, *args, **kwargs)

    patch_clients = mock.patch(
        "botocore.session.Session.create_client", new=create_client
    )
    patch_clients.start()

    original_make_request = botocore.endpoint.Endpoint.make_request

    @functools.wraps(original_make_request)
    def make_request(self, *args, **kwargs):
        if not self.host.startswith(endpoint_url):
            raise Exception()
        return original_make_request(self, *args, **kwargs)

    patch_requests = mock.patch(
        "botocore.endpoint.Endpoint.make_request", new=make_request
    )
    patch_requests.start()

    patch_status = mock.patch.object(aws_clients, "active", new=True)
    patch_status.start()
    try:
        yield
    finally:
        patch_clients.stop()
        patch_requests.stop()
        patch_status.stop()


aws_clients.active = False


@contextlib.contextmanager
def aws_credential_env_vars():
    """
    A context manager function that patches environment variables to set
    AWS credential env vars to dummy values.

    This should be done at the beginning of any tests, before the code to be tested has
    even been imported. That way there is no possibility of real calls being made to AWS.
    """
    new_env = {
        "AWS_ACCESS_KEY_ID": constants.DEFAULT_AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": constants.DEFAULT_AWS_SECRET_ACCESS_KEY,
        "AWS_SESSION_TOKEN": constants.DEFAULT_AWS_SESSION_TOKEN,
    }
    patch_env_vars = mock.patch.dict("os.environ", new_env)
    patch_env_vars.start()
    patch_status = mock.patch.object(aws_credential_env_vars, "active", new=True)
    patch_status.start()
    try:
        yield
    finally:
        patch_env_vars.stop()
        patch_status.stop()


aws_credential_env_vars.active = False
