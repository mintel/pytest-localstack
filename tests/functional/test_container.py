"""Functional tests for pytest_localstack.container."""
import logging

from pytest_localstack import container

logger = logging.getLogger(__name__)


def test_DockerLogTailer_stdout(docker_client, caplog):
    """Test DockerLogTailer with stdout-only."""
    _do_DockerLogTailer_test(
        docker_client,
        caplog,
        "echo foo && echo bar 1>&2",
        logs=["foo"],
        does_not_log=["bar"],
        stdout=True,
        stderr=False,
    )


def test_DockerLogTailer_stderr(docker_client, caplog):
    """Test DockerLogTailer with stderr-only."""
    _do_DockerLogTailer_test(
        docker_client,
        caplog,
        "echo foo && echo bar 1>&2",
        logs=["bar"],
        does_not_log=["foo"],
        stdout=False,
        stderr=True,
    )


def test_DockerLogTailer_both(docker_client, caplog):
    """Test DockerLogTailer with both stdout and stderr."""
    _do_DockerLogTailer_test(
        docker_client,
        caplog,
        "echo foo && echo bar 1>&2",
        logs=["foo", "bar"],
        stdout=True,
        stderr=True,
    )


def _do_DockerLogTailer_test(
    docker_client, caplog, cmd, logs=(), does_not_log=(), **kwargs
):
    echo = docker_client.containers.run("busybox", ["sh", "-c", cmd], detach=True)
    try:
        tailer = container.DockerLogTailer(echo, logger, logging.INFO, **kwargs)
        with caplog.at_level(logging.INFO, logger=logger.name):
            tailer.start()
            echo.wait(timeout=1)
            tailer.join(timeout=1)
        if tailer.is_alive():
            raise Exception("DockerLogTailer didn't stop")
        if hasattr(tailer, "exception"):
            raise tailer.exception
        for line in logs:
            assert (logger.name, logging.INFO, line) in caplog.record_tuples
        for line in does_not_log:
            assert (logger.name, logging.INFO, line) not in caplog.record_tuples
    finally:
        # Can't just autoremove, or the logs might disappear before DockerLogTailer can start.
        echo.remove(force=True)
