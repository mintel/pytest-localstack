"""Functional tests for pytest_localstack.session."""
import pytest

from pytest_localstack import constants, exceptions, service_checks, session


@pytest.mark.parametrize("test_service", sorted(constants.SERVICE_PORTS))
def test_RunningSession_individual_services(test_service, docker_client):
    localstack_imagename = "localstack/localstack:latest"

    docker_client.images.pull(localstack_imagename)
    localstack_container = None
    try:
        port = constants.SERVICE_PORTS[test_service]
        localstack_container = docker_client.containers.run(
            localstack_imagename,
            name="localstack_test",
            detach=True,
            auto_remove=True,
            ports={port: port},
        )
        test_session = session.RunningSession("127.0.0.1", services=[test_service])
        with test_session:
            for service_name, service_check in service_checks.SERVICE_CHECKS.items():
                if service_name == test_service:
                    service_check(test_session)
                else:
                    with pytest.raises(exceptions.ServiceError):
                        test_session.service_hostname(test_session)
    finally:
        if localstack_container:
            localstack_container.stop(timeout=10)


@pytest.mark.parametrize("test_service", sorted(constants.SERVICE_PORTS))
def test_LocalstackSession_individual_services(test_service, docker_client):
    """Test that each service can run individually."""
    test_session = session.LocalstackSession(docker_client, services=[test_service])
    with test_session:
        for service_name, service_check in service_checks.SERVICE_CHECKS.items():
            if service_name == test_service:
                service_check(test_session)
            else:
                with pytest.raises(exceptions.ServiceError):
                    test_session.service_hostname(test_session)
