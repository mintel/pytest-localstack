import logging
from enum import auto
from typing import TYPE_CHECKING, Union
from unittest import mock

import docker
import docker.errors

import pytest

from pytest_localstack import container, patch, utils


LOGGER = logging.getLogger(__name__)
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
LOGGER.addHandler(logging.NullHandler())


if TYPE_CHECKING:
    import _pytest.config
    import _pytest.config.argparsing

_start_timeout: float
_stop_timeout: float
_image: str
_pull: bool


def pytest_addoption(parser: "_pytest.config.argparsing.Parser"):
    """Hook to add pytest_localstack command line options to pytest."""
    group = parser.getgroup("localstack")
    group.addoption(
        "--localstack-image",
        action="store",
        type=str,
        default="localstack/localstack:latest",
        help="The Localstack Docker image to use for mocking AWS in tests.",
    )
    group.addoption(
        "--localstack-pull-image",
        action="store_true",
        help="If set, always pull the latest Localstack Docker image.",
    )
    group.addoption(
        "--localstack-start-timeout",
        action="store",
        type=float,
        default=60,
        help="The default max seconds for starting a localstack container.",
    )
    group.addoption(
        "--localstack-stop-timeout",
        action="store",
        type=float,
        default=10,
        help="The default max seconds for stopping a localstack container.",
    )


def pytest_configure(config: "_pytest.config.Config"):
    global _start_timeout, _stop_timeout, _image, _pull
    _start_timeout = config.getoption("--localstack-start-timeout")
    _stop_timeout = config.getoption("--localstack-stop-timeout")
    _image = config.getoption("--localstack-image")
    _pull = config.getoption("--localstack-pull-image")


@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()


@pytest.fixture(scope="session")
def localstack_image(docker_client: docker.DockerClient):
    image = None
    try:
        image = docker_client.images.get(_image)
    except docker.errors.ImageNotFound:
        pass
    if _pull or image is None:
        image = docker_client.images.pull(*(_image.split(":", 1)))
    return image


@pytest.fixture(scope="session", autouse=True)
def patch_aws_env_vars():
    with patch.aws_credential_env_vars():
        yield


def patch_aws_clients_fixture(
    endpoint_url: str,
    scope: str = "session",
    autouse: bool = False,
    verify_ssl: Union[bool, str] = False,
) -> pytest.fixture:
    @pytest.fixture(scope=scope, autouse=autouse)  # type: ignore
    def _fixture():
        with patch.aws_clients(endpoint_url, verify_ssl):
            yield

    return _fixture


# def patch_fixture(
#     scope: str = "function",
#     autouse: bool = False,
#     image: str = "localstack/localstack:latest",
#     container: Optional[str] = None,
#     auto_remove: bool = True,
#     pull_image: bool = True,
#     container_name: Optional[str] = None,
#     docker_client: Optional[docker.DockerClient] = None,
#     container_log_level: int = logging.DEBUG,
#     **kwargs,
# ):
#     """Create a pytest fixture that temporarily redirects all botocore
#     sessions and clients to a Localstack container.

#     This is not a fixture! It is a factory to create them.

#     The fixtures that are created by this function will run a Localstack
#     container and patch botocore to direct traffic there for the duration
#     of the tests.

#     Since boto3 uses botocore to send requests, boto3 will also be redirected.

#     Args:
#         scope (str, optional): The pytest scope which this fixture will use.
#             Defaults to :const:`"function"`.
#         services (list, dict, optional): One of

#             - A :class:`list` of AWS service names to start in the
#               Localstack container.
#             - A :class:`dict` of service names to the port they should run on.

#             Defaults to all services. Setting this
#             can reduce container startup time and therefore test time.
#         autouse (bool, optional): If :obj:`True`, automatically use this
#             fixture in applicable tests. Default: :obj:`False`
#         docker_client (:class:`~docker.client.DockerClient`, optional):
#             Docker client to run the Localstack container with.
#             Defaults to :func:`docker.client.from_env`.
#         region_name (str, optional): Region name to assume.
#             Each Localstack container acts like a single AWS region.
#             Defaults to :const:`"us-east-1"`.
#         kinesis_error_probability (float, optional): Decimal value between
#             0.0 (default) and 1.0 to randomly inject
#             ProvisionedThroughputExceededException errors
#             into Kinesis API responses.
#         dynamodb_error_probability (float, optional): Decimal value
#             between 0.0 (default) and 1.0 to randomly inject
#             ProvisionedThroughputExceededException errors into
#             DynamoDB API responses.
#         container_log_level (int, optional): The logging level to use
#             for Localstack container logs. Defaults to :data:`logging.DEBUG`.
#         localstack_version (str, optional): The version of the Localstack
#             image to use. Defaults to :const:`"latest"`.
#         auto_remove (bool, optional): If :obj:`True`, delete the Localstack
#             container when it stops. Default: :obj:`True`
#         pull_image (bool, optional): If :obj:`True`, pull the Localstack
#             image before running it. Default: :obj:`True`
#         container_name (str, optional): The name for the Localstack
#             container. Defaults to a randomly generated id.
#         **kwargs: Additional kwargs will be passed to the
#             :class:`.LocalstackSession`.

#     Returns:
#         A :func:`pytest fixture <_pytest.fixtures.fixture>`.

#     """

#     @pytest.fixture(scope=scope, autouse=autouse)  # type: ignore
#     def _fixture(pytestconfig):
#         if not pytestconfig.pluginmanager.hasplugin("localstack"):
#             pytest.skip("skipping because localstack plugin isn't loaded")
#         with _make_session(
#             docker_client=docker_client,
#             services=services,
#             region_name=region_name,
#             kinesis_error_probability=kinesis_error_probability,
#             dynamodb_error_probability=dynamodb_error_probability,
#             container_log_level=container_log_level,
#             localstack_version=localstack_version,
#             auto_remove=auto_remove,
#             pull_image=pull_image,
#             container_name=container_name,
#             **kwargs,
#         ) as session:
#             with session.botocore.patch_botocore():
#                 yield session

#     return _fixture


# def session_fixture(
#     scope: str = "function",
#     services: Optional[Union[List[str], Dict[str, int]]] = None,
#     autouse: bool = False,
#     docker_client: Optional[docker.DockerClient] = None,
#     region_name: Optional[str] = None,
#     kinesis_error_probability: float = 0.0,
#     dynamodb_error_probability: float = 0.0,
#     container_log_level: int = logging.DEBUG,
#     localstack_version: str = "latest",
#     auto_remove: bool = True,
#     pull_image: bool = True,
#     container_name: Optional[str] = None,
#     **kwargs,
# ):
#     """Create a pytest fixture that provides a LocalstackSession.

#     This is not a fixture! It is a factory to create them.

#     The fixtures that are created by this function will yield
#     a :class:`.LocalstackSession` instance.
#     This is useful for simulating multiple AWS accounts.
#     It does not automatically redirect botocore/boto3 traffic to Localstack
#     (although :class:`.LocalstackSession` has a method to do that.)

#     Args:
#         scope (str, optional): The pytest scope which this fixture will use.
#             Defaults to :const:`"function"`.
#         services (list, optional): One of:

#             - A :class:`list` of AWS service names to start in the
#               Localstack container.
#             - A :class:`dict` of service names to the port they should run on.

#             Defaults to all services. Setting this can reduce container
#             startup time and therefore test time.
#         autouse (bool, optional): If :obj:`True`, automatically use this
#             fixture in applicable tests. Default: :obj:`False`
#         docker_client (:class:`~docker.client.DockerClient`, optional):
#             Docker client to run the Localstack container with.
#             Defaults to :func:`docker.client.from_env`.
#         region_name (str, optional): Region name to assume.
#             Each Localstack container acts like a single AWS region.
#             Defaults to :const:`"us-east-1"`.
#         kinesis_error_probability (float, optional): Decimal value between
#             0.0 (default) and 1.0 to randomly inject
#             ProvisionedThroughputExceededException errors
#             into Kinesis API responses.
#         dynamodb_error_probability (float, optional): Decimal value
#             between 0.0 (default) and 1.0 to randomly inject
#             ProvisionedThroughputExceededException errors into
#             DynamoDB API responses.
#         container_log_level (int, optional): The logging level to use
#             for Localstack container logs. Defaults to :data:`logging.DEBUG`.
#         localstack_version (str, optional): The version of the Localstack
#             image to use. Defaults to :const:`"latest"`.
#         auto_remove (bool, optional): If :obj:`True`, delete the Localstack
#             container when it stops. Default: :obj:`True`
#         pull_image (bool, optional): If :obj:`True`, pull the Localstack
#             image before running it. Default: :obj:`True`.
#         container_name (str, optional): The name for the Localstack
#             container. Defaults to a randomly generated id.
#         **kwargs: Additional kwargs will be passed to the
#             :class:`.LocalstackSession`.

#     Returns:
#         A :func:`pytest fixture <_pytest.fixtures.fixture>`.

#     """

#     @pytest.fixture(scope=scope, autouse=autouse)  # type: ignore
#     def _fixture(pytestconfig: "_pytest.config.Config"):
#         if not pytestconfig.pluginmanager.hasplugin("localstack"):
#             pytest.skip("skipping because localstack plugin isn't loaded")
#         with _make_session(
#             docker_client=docker_client,
#             services=services,
#             region_name=region_name,
#             kinesis_error_probability=kinesis_error_probability,
#             dynamodb_error_probability=dynamodb_error_probability,
#             container_log_level=container_log_level,
#             localstack_version=localstack_version,
#             auto_remove=auto_remove,
#             pull_image=pull_image,
#             container_name=container_name,
#             **kwargs,
#         ) as session:
#             yield session

#     return _fixture


# @contextlib.contextmanager
# def _make_session(docker_client: Optional[docker.DockerClient], *args, **kwargs):
#     utils.check_proxy_env_vars()

#     if docker_client is None:
#         docker_client = docker.from_env()

#     try:
#         docker_client.ping()  # Check connectivity
#     except docker.errors.APIError:
#         pytest.fail("Could not connect to Docker.")

#     _session = session.LocalstackSession(docker_client, *args, **kwargs)

#     _session.start(timeout=_start_timeout)
#     try:
#         yield _session
#     finally:
#         _session.stop(timeout=_stop_timeout)
