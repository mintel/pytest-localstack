"""Test utils."""
import hashlib

import docker

from pytest_localstack import session
from pytest_localstack.utils import mock

AWS_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-south-1",
    "sa-east-1",
]


def generate_fake_logs(n=10):
    """Generate some fake log lines."""
    for i in range(n):
        yield "foobar {}\n".format(i).encode("utf-8")


def make_mock_container(
    image, command=None, stdout=True, stderr=False, remove=False, **kwargs
):
    """Make a mock docker-py Container object."""
    container = mock.Mock(spec=docker.models.containers.Container)
    container.labels = []
    container.status = "running"
    container.name = kwargs.get("name") or session.generate_container_name()
    container.id = (
        "sha256:" + hashlib.sha256(container.name.encode("utf-8")).hexdigest()
    )
    container.short_id = container.id.split(":")[1][:6]

    def _stop(timeout=10):
        container.status = "exited"

    container.stop.side_effect = _stop

    def _logs(
        stdout=True,
        stderr=True,
        stream=False,
        timestamps=False,
        tail="all",
        since=None,
        follow=None,
    ):
        logs_generator = generate_fake_logs()
        if stream:
            return logs_generator
        else:
            return b"".join(logs_generator)

    container.logs.side_effect = _logs
    return container


def make_mock_docker_client():
    """Make a mock docker-py Client object."""
    docker_client = mock.Mock(spec=docker.client.DockerClient)
    containers = docker_client.containers
    containers.run.side_effect = make_mock_container
    docker_client.api = mock.Mock(spec=docker.api.APIClient)
    docker_client.api.port.side_effect = lambda cid, port: [{"HostPort": port}]
    return docker_client


def make_test_LocalstackSession(*args, **kwargs):
    """Make a test LocalstackSession that doesn't actually run Localstack."""
    docker_client = make_mock_docker_client()
    test_session = session.LocalstackSession(docker_client, *args, **kwargs)

    test_session._check_services = mock.Mock(
        return_value=None,
        __name__=test_session._check_services.__name__,
        __code__=test_session._check_services.__code__,
    )

    return test_session


def make_test_RunningSession(*args, **kwargs):
    """Make a test RunningSession that isn't actually connected to Localstack."""
    test_session = session.RunningSession("127.0.0.1", *args, **kwargs)

    test_session._check_services = mock.Mock(
        return_value=None,
        __name__=test_session._check_services.__name__,
        __code__=test_session._check_services.__code__,
    )

    return test_session
