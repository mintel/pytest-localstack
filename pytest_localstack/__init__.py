import contextlib
import logging
import sys

import docker

import pytest

from pytest_localstack import plugin, session, utils


_start_timeout = None
_stop_timeout = None


def pytest_configure(config):
    global _start_timeout, _stop_timeout
    _start_timeout = config.getoption("--localstack-start-timeout")
    _stop_timeout = config.getoption("--localstack-stop-timeout")


def pytest_addoption(parser):
    """Hook to add pytest_localstack command line options to pytest."""
    group = parser.getgroup("localstack")
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


def session_fixture(
    scope="function",
    services=None,
    autouse=False,
    docker_client=None,
    region_name=None,
    kinesis_error_probability=0.0,
    dynamodb_error_probability=0.0,
    container_log_level=logging.DEBUG,
    localstack_version="latest",
    auto_remove=True,
    pull_image=True,
    container_name=None,
    **kwargs
):
    """Create a pytest fixture that provides a LocalstackSession.

    This is not a fixture! It is a factory to create them.

    The fixtures that are created by this function will yield
    a :class:`.LocalstackSession` instance.
    This is useful for simulating multiple AWS accounts.
    It does not automatically redirect botocore/boto3 traffic to Localstack
    (although :class:`.LocalstackSession` has a method to do that.)

    Args:
        scope (str, optional): The pytest scope which this fixture will use.
            Defaults to :const:`"function"`.
        services (list, dict, optional): One of:

            - A :class:`list` of AWS service names to start in the
              Localstack container.
            - A :class:`dict` of service names to the port they should run on.

            Defaults to all services. Setting this can reduce container
            startup time and therefore test time.
        autouse (bool, optional): If :obj:`True`, automatically use this
            fixture in applicable tests. Default: :obj:`False`
        docker_client (:class:`~docker.client.DockerClient`, optional):
            Docker client to run the Localstack container with.
            Defaults to :func:`docker.client.from_env`.
        region_name (str, optional): Region name to assume.
            Each Localstack container acts like a single AWS region.
            Defaults to :const:`"us-east-1"`.
        kinesis_error_probability (float, optional): Decimal value between
            0.0 (default) and 1.0 to randomly inject
            ProvisionedThroughputExceededException errors
            into Kinesis API responses.
        dynamodb_error_probability (float, optional): Decimal value
            between 0.0 (default) and 1.0 to randomly inject
            ProvisionedThroughputExceededException errors into
            DynamoDB API responses.
        container_log_level (int, optional): The logging level to use
            for Localstack container logs. Defaults to :data:`logging.DEBUG`.
        localstack_version (str, optional): The version of the Localstack
            image to use. Defaults to :const:`"latest"`.
        auto_remove (bool, optional): If :obj:`True`, delete the Localstack
            container when it stops. Default: :obj:`True`
        pull_image (bool, optional): If :obj:`True`, pull the Localstack
            image before running it. Default: :obj:`True`.
        container_name (str, optional): The name for the Localstack
            container. Defaults to a randomly generated id.
        **kwargs: Additional kwargs will be passed to the
            :class:`.LocalstackSession`.

    Returns:
        A :func:`pytest fixture <_pytest.fixtures.fixture>`.

    """

    @pytest.fixture(scope=scope, autouse=autouse)
    def _fixture(pytestconfig):
        if not pytestconfig.pluginmanager.hasplugin("localstack"):
            pytest.skip("skipping because localstack plugin isn't loaded")
        with _make_session(
            docker_client=docker_client,
            services=services,
            region_name=region_name,
            kinesis_error_probability=kinesis_error_probability,
            dynamodb_error_probability=dynamodb_error_probability,
            container_log_level=container_log_level,
            localstack_version=localstack_version,
            auto_remove=auto_remove,
            pull_image=pull_image,
            container_name=container_name,
            **kwargs
        ) as session:
            yield session

    return _fixture


@contextlib.contextmanager
def _make_session(docker_client, *args, **kwargs):
    utils.check_proxy_env_vars()

    if docker_client is None:
        docker_client = docker.from_env()

    try:
        docker_client.ping()  # Check connectivity
    except docker.errors.APIError:
        pytest.fail("Could not connect to Docker.")

    _session = session.LocalstackSession(docker_client, *args, **kwargs)

    _session.start(timeout=_start_timeout)
    try:
        yield _session
    finally:
        _session.stop(timeout=_stop_timeout)


# Register contrib modules
plugin.register_plugin_module("pytest_localstack.contrib.botocore")
plugin.register_plugin_module("pytest_localstack.contrib.boto3", False)

# Register 3rd-party modules
plugin.manager.load_setuptools_entrypoints("localstack")

# Trigger pytest_localstack_contribute_to_module hook
plugin.manager.hook.contribute_to_module.call_historic(
    kwargs={"pytest_localstack": sys.modules[__name__]}
)
