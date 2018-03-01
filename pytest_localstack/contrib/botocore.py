"""pytest-localstack extensions for botocore."""
from __future__ import print_function

import contextlib
import logging

from pytest_localstack.hookspecs import pytest_localstack_hookimpl

# import botocore


logger = logging.getLogger(__name__)


@pytest_localstack_hookimpl
def contribute_to_session(session):
    """Add :class:`BotocoreTestResourceFactory` to :class:`LocalstackSession`."""
    logger.debug('patching session {!r}'.format(session))
    session.botocore = BotocoreTestResourceFactory(session)
    session.patch = session.botocore.patch_session


@pytest_localstack_hookimpl
def contribute_to_module(pytest_localstack):
    """Add :func:`patch_fixture` to :mod:`pytest_localstack`."""
    logger.debug('patching module {!r}'.format(pytest_localstack))
    pytest_localstack.patch_fixture = patch_fixture


class BotocoreTestResourceFactory(object):
    """Create botocore clients to interact with a :class:`LocalstackSession`."""

    def __init__(self, session):
        logger.debug('BotocoreTestResourceFactory.__init__')
        self.session = session

    @contextlib.contextmanager
    def patch_session(self, session):
        """Batch botocore clients/sessions to use the Localstack container in `session`."""
        logger.debug("enter patch")
        try:
            yield
        finally:
            logger.debug("exit patch")


def patch_fixture():
    """Pytest fixture that runs Localstack and patches botocore to use it."""
    # TODO: implement
    raise NotImplementedError
