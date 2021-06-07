import logging
import os
import threading
from typing import Dict, Optional, Union

import docker
import requests
from docker.models.containers import Container
from docker.types import CancellableStream

from pytest_localstack import constants, utils


LOGGER = logging.getLogger(__name__)


class LocalstackContainer:
    """Manages a Docker container running Localstack."""

    @classmethod
    def start(
        cls,
        image: str = "localstack/localstack:latest",
        docker_client: Optional[docker.DockerClient] = None,
        auto_remove: bool = True,
        environment: Optional[Dict[str, str]] = None,
        container_name: Optional[str] = None,
    ):
        """Run a Localstack container.

        Args:
            image (str, optional): The Localstack Docker image to run.
                Defaults to "localstack/localstack:latest".
            pull_image (bool, optional): If the image should be pulled to get the latest version
                before being run. Defaults to True.
            docker_client (docker.DockerClient, optional): The Docker API client.
                If not specified, one is created with default settings.
                Defaults to creating a new client from the Docker defaults.
            auto_remove (bool, optional): If true, delete the Localstack container after it exits.
                Defaults to True.
            environment (Dict[str, str], optional): A dict of additional
                configuration to pass as environment variables to the container.
                See: https://github.com/localstack/localstack#configurations
                Defaults to None.
            container_name (str, optional): A name for the Localstack container.
                Defaults to a randomly generate name like "pytest-localstack-abc123".
        Returns:
            LocalstackContainer: The running Localstack container.
        """

        utils.check_supported_localstack_image(image)

        if docker_client is None:
            docker_client = docker.from_env()

        if container_name is None:
            container_name = f"pytest-localstack-{utils.generate_random_string()}"

        if environment is not None and "AWS_DEFAULT_REGION" in os.environ:
            # Honor the AWS_DEFAULT_REGION env var by running the
            # Localstack container as the same region, unless
            # the desired region was passed in explicitly.
            environment.setdefault("DEFAULT_REGION", os.environ["AWS_DEFAULT_REGION"])

        LOGGER.debug("Starting container '%s'", container_name)
        container = docker_client.containers.run(
            image,
            name=container_name,
            detach=True,
            auto_remove=auto_remove,
            environment=environment,
            ports={
                f"{constants.EDGE_PORT}/tcp": None,  # 4566
                f"{constants.ELASTICSEARCH_PORT}/tcp": None,  # 4571
                f"{constants.WEB_UI_PORT}/tcp": None,  # 8080
                f"{constants.DEVELOP_PORT}/tcp": None,  # 5678
            },
        )
        return cls(container)

    @classmethod
    def from_existing(
        cls, container_id: str, docker_client: Optional[docker.DockerClient] = None
    ):
        """Return a LocalstackContainer for an already-running container.

        Args:
            container_id (str): The ID or name of an already-running Localstack container.
            docker_client (docker.DockerClient, optional): The Docker API client.
                If not specified, one is created with default settings.
                Defaults to creating a new client from the Docker defaults.
        Returns:
            LocalstackContainer: The running Localstack container.
        """
        if docker_client is None:
            docker_client = docker.from_env()
        return LocalstackContainer(docker_client.containers.get(container_id))

    def __init__(self, container: Container):
        self.container = container
        self._logger = LOGGER.getChild(f"containers.{self.container.name}")

    def is_ready(self) -> bool:
        """Returns True if all Localstack services and features are ready."""
        try:
            resp = requests.get(f"http://localhost:{self.get_edge_host_port()}/health")
        except requests.ConnectionError:
            self._logger.debug(
                "Localstack not ready; healthcheck endpoint connection error."
            )
            return False
        body = resp.json()

        if "services" not in body:
            self._logger.debug(
                "Localstack not ready; service status isn't populated yet."
            )
            return False

        if "features" not in body:
            self._logger.debug(
                "Localstack not ready; feature status isn't populated yet."
            )
            return False

        if "initScripts" not in body["features"]:
            self._logger.debug(
                "Localstack not ready; initScripts status isn't populated yet."
            )
            return False

        if "persistence" not in body["features"]:
            self._logger.debug(
                "Localstack not ready; persistence status isn't populated yet."
            )
            return False

        for feature, status in body["features"].items():
            if status not in ("initialized", "disabled"):
                self._logger.debug(
                    "Localstack not ready; feature '%s' is '%s', must be 'initialized' or 'disabled'.",
                    feature,
                    status,
                )
                return False

        for service, status in body["services"].items():
            if status != "running":
                self._logger.debug(
                    "Localstack not ready; service '%s' is '%s', not 'running'.",
                    service,
                    status,
                )
                return False

        return True

    def wait_for_ready(self, timeout: float = 60, poll_interval: float = 0.25) -> None:
        """Wait until all Localstack services and features are ready or timeout is reached.

        Args:
            timeout (float, optional): [description]. Defaults to 60.
            poll_interval (float, optional): [description]. Defaults to 0.25.
        Raises:
            TimeoutError: if the timeout is reached before Localstack is ready.
        """
        done = threading.Event()

        def _poll():
            while not done.is_set():
                ready = self.is_ready()
                if ready:
                    done.set()
                    return
                done.wait(poll_interval)

        t = threading.Thread(target=_poll, daemon=True)
        t.start()
        try:
            done.wait(timeout)
        finally:
            done.set()

    def stop(self, timeout: Optional[int] = 10):
        """
        Stop the Localstack container.

        Will wait `timeout` seconds for the container to exit
        gracefully before SIGKILLing it.
        """
        self.container.stop(timeout=timeout)

    def tail_logs(
        self, logger: logging.Logger = LOGGER, level: int = logging.INFO
    ) -> None:
        """Tail the container's logs, sending each line to `logger`."""
        container_logger = logger.getChild("containers.%s" % self.container.short_id)

        stdout_tailer = DockerLogTailer(
            self.container,
            container_logger.getChild("stdout"),
            level,
            stdout=True,
            stderr=False,
        )
        stdout_tailer.start()

        stderr_tailer = DockerLogTailer(
            self.container,
            container_logger.getChild("stderr"),
            level,
            stdout=False,
            stderr=True,
        )
        stderr_tailer.start()

    @property
    def _docker_client(self) -> docker.DockerClient:
        return self.container.client

    def get_environment(self) -> Dict[str, str]:
        """Return a dict of the container environment variables."""
        env = {}
        for env_pair in self.container.attrs["Config"]["Env"]:
            key, value = env_pair.split("=", 1)
            env[key] = value
        return env

    def get_host_port(self, port: int) -> Optional[int]:
        """Gets a host port number from a container port number."""
        result = self._docker_client.api.port(self.container.id, port)
        if not result:
            return None
        return int(result[0]["HostPort"])

    def get_edge_host_port(self) -> int:
        """The port on the host machine where AWS services can be accessed."""
        return self.get_host_port(constants.EDGE_PORT)

    def get_elasticsearch_host_port(self) -> int:
        """The port on the host machine where Elasticsearch can be accessed, if it's running."""
        return self.get_host_port(constants.ELASTICSEARCH_PORT)

    def get_web_ui_host_port(self) -> int:
        """The port on the host machine where the Localstack web UI can be accessed."""
        return self.get_host_port(constants.WEB_UI_PORT)

    def get_develop_host_port(self) -> int:
        """The port on the host machine where debugpy can be access, if the DEVELOP=true env var was set."""
        return self.get_host_port(constants.DEVELOP_PORT)

    def get_edge_url(self) -> str:
        """Get a full URL to the Localstack edge endpoint.
        This is the URL that would be use as the endpoint URL
        of test AWS clients.
        """
        host = "localhost"
        port = self.get_edge_host_port()
        if "USE_SSL" in self.get_environment():
            proto = "https"
        else:
            proto = "http"
        return f"{proto}://{host}:{port}"


class DockerLogTailer(threading.Thread):
    """Write Docker container logs to a Python logger, as a separate thread.

    If there's an exception that causes the thread to exit, it will
    be stored as an `exception` attribute.

    Args:
        container: A container object returned by docker-py's `run(detach=True)`
            method.
        logger: A standard Python logger.
        log_level: The log level to use.
        stdout: Capture the containers stdout logs. Default is True.
        stderr: Capture the containers stderr logs. Default is True.
        encoding: Read container logs bytes using this encoding. Default is utf-8. Set
            to None to log raw bytes.
        tail: The number of line to to emit from the end of the existing container logs
            when start() is called. Can be any int number of log lines or the string
            `all` to emit all existing lines.

    """

    container: Container
    logger: logging.Logger
    log_level: int
    stdout: bool
    stderr: bool
    encoding: str
    tail: Union[int, str]
    _logs_generator: Optional[CancellableStream]
    exception: Optional[Exception]

    def __init__(
        self,
        container: Container,
        logger: logging.Logger,
        log_level: int,
        stdout: bool = True,
        stderr: bool = True,
        encoding: str = "utf-8",
        tail: Union[int, str] = 0,
    ):
        self.container = container
        self.logger = logger
        self.log_level = log_level
        self.stdout = stdout
        self.stderr = stderr
        self.encoding = encoding
        self.tail = tail
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            self._logs_generator = self.container.logs(
                stream=True,
                stdout=self.stdout,
                stderr=self.stderr,
                follow=True,
                tail=self.tail,
            )
            for line in self._logs_generator:
                if self.encoding is not None and isinstance(line, bytes):
                    line = line.decode(self.encoding)
                line = utils.remove_newline(line)
                self.logger.log(self.log_level, line)
        except Exception as e:
            self.exception = e
            raise

    def stop(self):
        """Stop tailing the logs."""
        if self._logs_generator is None:
            raise RuntimeError("DockerLogTailer isn't started yet")
        self._logs_generator.close()
