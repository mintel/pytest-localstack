import pytest_localstack
from pytest_localstack import hookspecs, plugin


@hookspecs.pytest_localstack_hookimpl
def contribute_to_module(pytest_localstack):
    pytest_localstack._foo = "bar"


def test_register_plugin_module():
    assert not hasattr(pytest_localstack, "_foo")
    plugin.register_plugin_module("tests.integration.test_plugin")
    assert pytest_localstack._foo == "bar"
    del pytest_localstack._foo
