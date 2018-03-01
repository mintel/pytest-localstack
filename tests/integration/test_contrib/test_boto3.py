from pytest_localstack import plugin
from pytest_localstack.contrib import boto3 as ptls_boto3


def test_session_contribution():
    dummy_session = type('DummySession', (object,), {})()
    plugin.manager.hook.contribute_to_session(session=dummy_session)
    assert isinstance(dummy_session.boto3, ptls_boto3.Boto3TestResourceFactory)
