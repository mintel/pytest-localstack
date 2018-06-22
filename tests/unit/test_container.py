import logging

from tests import utils as test_utils

from pytest_localstack import container as ptls_container, session
from pytest_localstack.utils import mock


def test_DockerLogTailer(caplog):
    """Test pytest_localstack.container.DockerLogTailer."""
    container = test_utils.make_mock_container(session.LocalstackSession.image_name)
    logger_name = "test_logger.%s." % container.short_id
    logger = logging.getLogger(logger_name)
    log_level = logging.DEBUG
    tailer = ptls_container.DockerLogTailer(
        container,
        logger,
        log_level,
        stdout=mock.sentinel.stdout,
        stderr=mock.sentinel.stderr,
    )
    with caplog.at_level(logging.DEBUG, logger=logger.name):
        tailer.start()
        tailer.join(1)
        if tailer.is_alive():
            raise Exception("DockerLogTailer never stopped!")
        container.logs.assert_called_once_with(
            stdout=mock.sentinel.stdout, stderr=mock.sentinel.stderr, stream=True
        )
        for log_line in test_utils.generate_fake_logs():
            log_line = log_line.decode("utf-8").rstrip()
            assert (logger_name, log_level, log_line) in caplog.record_tuples
