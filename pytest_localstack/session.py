"""Run and interact with a Localstack container."""
import logging

from pytest_localstack import plugin

logger = logging.getLogger(__name__)

DEFAULT_START_TIMEOUT = 60
DEFAULT_STOP_TIMEOUT = 10


class LocalstackSession(object):
    """Run and interact with a Localstack container."""

    def __init__(self):
        plugin.manager.hook.contribute_to_session(session=self)

    def start(self, timeout=DEFAULT_START_TIMEOUT):
        """Start Localstack container."""
        logger.debug('starting {!r}'.format(self))
        plugin.manager.hook.session_starting(session=self)
        logger.debug('started {!r}'.format(self))
        plugin.manager.hook.session_started(session=self)

    def stop(self, timeout=DEFAULT_STOP_TIMEOUT):
        """Stop Localstack container."""
        logger.debug('stopping {!r}'.format(self))
        plugin.manager.hook.session_stopping(session=self)
        logger.debug('stopped {!r}'.format(self))
        plugin.manager.hook.session_stopped(session=self)

    def __enter__(self, start_timeout=DEFAULT_START_TIMEOUT,
                  stop_timeout=DEFAULT_STOP_TIMEOUT):
        self.__stop_timeout = stop_timeout
        self.start(timeout=start_timeout)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop(timeout=self.__stop_timeout)
        del self.__stop_timeout
