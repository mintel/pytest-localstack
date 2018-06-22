import os

import boto3
import botocore

import pytest
from tests import utils as test_utils

from pytest_localstack import constants, exceptions, plugin
from pytest_localstack.contrib import boto3 as ptls_boto3
from pytest_localstack.utils import mock


def test_session_contribution():
    dummy_session = type("DummySession", (object,), {})()
    plugin.manager.hook.contribute_to_session(session=dummy_session)
    assert isinstance(dummy_session.boto3, ptls_boto3.Boto3TestResourceFactory)


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
def test_session(make_test_session):
    """Test session creation."""
    localstack = make_test_session()

    ls_session = localstack.boto3.session()
    assert isinstance(ls_session, boto3.session.Session)


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
def test_default_session(make_test_session):
    """Test default session."""
    localstack = make_test_session()
    session_1 = localstack.boto3.default_session
    session_2 = localstack.boto3.default_session
    assert session_1 is session_2


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_client(service_name, make_test_session):
    """Test client creation."""
    localstack = make_test_session()
    if hasattr(localstack, "_container"):
        with pytest.raises(exceptions.ContainerNotStartedError):
            client = localstack.boto3.client(service_name)

    with localstack:
        client = localstack.boto3.client(service_name)
        assert isinstance(client, botocore.client.BaseClient)
        assert "127.0.0.1" in client._endpoint.host


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_resource(service_name, make_test_session):
    """Test resource creation."""
    if service_name not in [
        "cloudformation",
        "cloudwatch",
        "dynamodb",
        "ec2",
        "glacier",
        "iam",
        "opsworks",
        "s3",
        "sns",
        "sqs",
    ]:
        pytest.skip("No boto3 resource available for this service.")
    localstack = make_test_session()

    if hasattr(localstack, "_container"):
        with pytest.raises(exceptions.ContainerNotStartedError):
            resource = localstack.boto3.resource(service_name)

    with localstack:
        resource = localstack.boto3.resource(service_name)
        assert isinstance(resource, boto3.resources.base.ServiceResource)
        assert "127.0.0.1" in resource.meta.client._endpoint.host


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
def test_patch_botocore_credentials(make_test_session):
    """Test to the default boto3 session credentials get patched correctly."""
    session = boto3._get_default_session()
    localstack = make_test_session()

    credentials = session.get_credentials()
    initial_access_key = credentials.access_key if credentials else None
    initial_secret_key = credentials.secret_key if credentials else None
    initial_token = credentials.token if credentials else None
    initial_method = credentials.method if credentials else None

    assert initial_access_key != constants.DEFAULT_AWS_ACCESS_KEY_ID
    assert initial_secret_key != constants.DEFAULT_AWS_SECRET_ACCESS_KEY
    assert initial_token != constants.DEFAULT_AWS_SESSION_TOKEN
    assert initial_method != "localstack-default"

    with localstack:
        # should prefer access credentials from environment variables.
        with mock.patch.dict(
            os.environ,
            AWS_ACCESS_KEY_ID=str(mock.sentinel.AWS_ACCESS_KEY_ID),
            AWS_SECRET_ACCESS_KEY=str(mock.sentinel.AWS_SECRET_ACCESS_KEY),
            AWS_SESSION_TOKEN=str(mock.sentinel.AWS_SESSION_TOKEN),
        ):
            with localstack.botocore.patch_botocore():
                credentials = session.get_credentials()
                assert credentials is not None
                assert credentials.access_key == str(mock.sentinel.AWS_ACCESS_KEY_ID)
                assert credentials.secret_key == str(
                    mock.sentinel.AWS_SECRET_ACCESS_KEY
                )
                assert credentials.token == str(mock.sentinel.AWS_SESSION_TOKEN)
                assert credentials.method == "env"

        # check credentials get unpatched correctly
        credentials = session.get_credentials()
        assert (credentials.access_key if credentials else None) == initial_access_key
        assert (credentials.secret_key if credentials else None) == initial_secret_key
        assert (credentials.token if credentials else None) == initial_token
        assert (credentials.method if credentials else None) == initial_method

        # should fallback to default credentials if none in the environment
        with mock.patch.dict(
            os.environ,
            AWS_ACCESS_KEY_ID="",
            AWS_SECRET_ACCESS_KEY="",
            AWS_SESSION_TOKEN="",
        ):
            os.environ.pop("AWS_ACCESS_KEY_ID", None)
            os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
            os.environ.pop("AWS_SESSION_TOKEN", None)
            with localstack.botocore.patch_botocore():
                credentials = session.get_credentials()
                assert credentials is not None
                assert credentials.access_key == constants.DEFAULT_AWS_ACCESS_KEY_ID
                assert credentials.secret_key == constants.DEFAULT_AWS_SECRET_ACCESS_KEY
                assert credentials.token == constants.DEFAULT_AWS_SESSION_TOKEN
                assert credentials.method == "localstack-default"

        # check credentials get unpatched correctly
        credentials = session.get_credentials()
        assert (credentials.access_key if credentials else None) == initial_access_key
        assert (credentials.secret_key if credentials else None) == initial_secret_key
        assert (credentials.token if credentials else None) == initial_token
        assert (credentials.method if credentials else None) == initial_method
