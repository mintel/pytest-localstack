"""Docker container tools."""
import threading

from pytest_localstack import utils


class DockerLogTailer(threading.Thread):
    """Write Docker container logs to a Python standard logger.

    Args:
        container (:class:`docker.models.containers.Container`):
            A container object returned by docker-py's
            `run(detach=True)` method.
        logger (:class:`logging.Logger`): A standard Python logger.
        log_level (int): The log level to use.
        stdout (bool, optional): Capture the containers stdout logs.
            Default is True.
        stderr (bool, optional): Capture the containers stderr logs.
            Default is True.
        encoding (str, optional): Read container logs bytes using
            this encoding. Default is utf-8. Set to None to log raw bytes.

    """

    def __init__(
        self, container, logger, log_level, stdout=True, stderr=True, encoding="utf-8"
    ):
        self.container = container
        self.logger = logger
        self.log_level = log_level
        self.stdout = stdout
        self.stderr = stderr
        self.encoding = encoding
        super(DockerLogTailer, self).__init__()
        self.daemon = True

    def run(self):
        """Tail the container logs as a separate thread."""
        try:
            logs_generator = self.container.logs(
                stream=True, stdout=self.stdout, stderr=self.stderr
            )
            for line in logs_generator:
                if self.encoding is not None and isinstance(line, bytes):
                    line = line.decode(self.encoding)
                line = utils.remove_newline(line)
                self.logger.log(self.log_level, line)
        except Exception as e:
            self.exception = e
            raise
