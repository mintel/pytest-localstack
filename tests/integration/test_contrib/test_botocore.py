import pytest_localstack
from pytest_localstack import plugin
from pytest_localstack.contrib import botocore as ptls_botocore


def test_patch_fixture_contributed_to_module():
    assert pytest_localstack.patch_fixture is ptls_botocore.patch_fixture


def test_session_contribution():
    dummy_session = type('DummySession', (object,), {})()
    plugin.manager.hook.contribute_to_session(session=dummy_session)
    assert isinstance(dummy_session.botocore, ptls_botocore.BotocoreTestResourceFactory)
