import sys

from pytest_localstack import plugin
from pytest_localstack._version import __version__  # noqa: F401


def pytest_addoption(parser):
    """Hook to add pytest-localstack command line options to pytest."""
    group = parser.getgroup('pytest-localstack')
    group.addoption(
        "--no-localstack",
        action="store_true",
        default=False,
        help="skip tests with a pytest-localstack fixture",
    )
    group.addoption(
        "--localstack-start-timeout",
        action="store",
        type=int,
        default=60,
        help="max seconds for starting a localstack container",
    )
    group.addoption(
        "--localstack-stop-timeout",
        action="store",
        type=int,
        default=5,
        help="max seconds for stopping a localstack container",
    )


# Register contrib modules
plugin.register_plugin_module('pytest_localstack.contrib.botocore')
plugin.register_plugin_module('pytest_localstack.contrib.boto3', False)

# Register 3rd-party modules
plugin.manager.load_setuptools_entrypoints("pytest-localstack")

# Trigger pytest_localstack_contribute_to_module hook
plugin.manager.hook.contribute_to_module.call_historic(pytest_localstack=sys.modules[__name__])
