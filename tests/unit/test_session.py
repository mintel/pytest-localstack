import re
import time

import pytest
from hypothesis import given, strategies as st
from tests import utils as test_utils

from pytest_localstack import constants, exceptions, session


@given(random=st.random_module())
def test_generate_container_name(random):
    """Test pytest_localstack.session.generate_container_name."""
    result = session.generate_container_name()
    assert re.match(r"^pytest-localstack-[\w]{6}$", result)


@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_LocalstackSession_map_port(service_name):
    """Test pytest_localstack.session.LocalstackSession.map_port."""
    test_session = test_utils.make_test_LocalstackSession()

    port = constants.SERVICE_PORTS[service_name]

    with pytest.raises(exceptions.ContainerNotStartedError):
        test_session.map_port(port)

    test_session.start()
    result = test_session.map_port(port)
    assert result == port  # see tests.utils.make_mock_docker_client()


@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
@pytest.mark.parametrize("not_service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_LocalstackSession_service_hostname(service_name, not_service_name):
    """Test pytest_localstack.session.LocalstackSession.service_hostname."""
    if service_name == not_service_name:
        pytest.skip("should not be equal")

    test_session = test_utils.make_test_LocalstackSession(services=[service_name])

    with pytest.raises(exceptions.ContainerNotStartedError):
        test_session.service_hostname(service_name)

    test_session.start()

    with pytest.raises(exceptions.ServiceError):
        test_session.service_hostname(not_service_name)

    result = test_session.service_hostname(service_name)

    # see tests.utils.make_mock_docker_client()
    assert result == "127.0.0.1:%i" % (constants.SERVICE_PORTS[service_name])


@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
@pytest.mark.parametrize("not_service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_RunningSession_service_hostname(service_name, not_service_name):
    """Test pytest_localstack.session.RunningSession.service_hostname."""
    if service_name == not_service_name:
        pytest.skip("should not be equal")

    test_session = test_utils.make_test_RunningSession(services=[service_name])

    with pytest.raises(exceptions.ServiceError):
        test_session.service_hostname(not_service_name)

    result = test_session.service_hostname(service_name)

    # see tests.utils.make_mock_docker_client()
    assert result == "127.0.0.1:%i" % (constants.SERVICE_PORTS[service_name])


@pytest.mark.parametrize("use_ssl", [(True,), (False,)])
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
@pytest.mark.parametrize("not_service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_LocalstackSession_endpoint_url(use_ssl, service_name, not_service_name):
    """Test pytest_localstack.session.LocalstackSession.endpoint_url."""
    if service_name == not_service_name:
        pytest.skip("should not be equal")

    test_session = test_utils.make_test_LocalstackSession(
        services=[service_name], use_ssl=use_ssl
    )

    with pytest.raises(exceptions.ContainerNotStartedError):
        test_session.endpoint_url(service_name)

    test_session.start()

    with pytest.raises(exceptions.ServiceError):
        test_session.endpoint_url(not_service_name)

    result = test_session.endpoint_url(service_name)
    if test_session.use_ssl:
        # see tests.utils.make_mock_docker_client()
        assert result == "https://127.0.0.1:%i" % (
            constants.SERVICE_PORTS[service_name]
        )
    else:
        # see tests.utils.make_mock_docker_client()
        assert result == "http://127.0.0.1:%i" % (constants.SERVICE_PORTS[service_name])


@pytest.mark.parametrize("use_ssl", [(True,), (False,)])
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
@pytest.mark.parametrize("not_service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_RunningSession_endpoint_url(use_ssl, service_name, not_service_name):
    """Test pytest_localstack.session.RunningSession.endpoint_url."""
    if service_name == not_service_name:
        pytest.skip("should not be equal")

    test_session = test_utils.make_test_RunningSession(
        services=[service_name], use_ssl=use_ssl
    )

    with pytest.raises(exceptions.ServiceError):
        test_session.endpoint_url(not_service_name)

    result = test_session.endpoint_url(service_name)
    if test_session.use_ssl:
        # see tests.utils.make_mock_docker_client()
        assert result == "https://127.0.0.1:%i" % (
            constants.SERVICE_PORTS[service_name]
        )
    else:
        # see tests.utils.make_mock_docker_client()
        assert result == "http://127.0.0.1:%i" % (constants.SERVICE_PORTS[service_name])


def test_LocalstackSession_context():
    """Test pytest_localstack.session.LocalstackSession as a context manager."""
    test_session = test_utils.make_test_LocalstackSession()

    assert test_session._container is None
    with test_session:
        assert test_session._container is not None
        time.sleep(1)  # give fake like generator some time
    assert test_session._container is None


def test_LocalstackSession_start_timeout():
    """Test that the LocalstackSession.start() timeout works."""
    test_session = test_utils.make_test_LocalstackSession()

    test_session._check_services.side_effect = exceptions.ContainerNotStartedError(
        test_session
    )

    with pytest.raises(exceptions.ContainerNotStartedError):
        test_session.start(timeout=1)
