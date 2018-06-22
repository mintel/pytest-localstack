"""Configure pytest for the functional tests module."""
import docker

import pytest


@pytest.fixture(scope="module")
def docker_client():
    """Fixture to create a local Docker client."""
    return docker.from_env()
