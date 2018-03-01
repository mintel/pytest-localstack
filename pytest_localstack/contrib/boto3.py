"""pytest-localstack extensions for boto3."""
from __future__ import print_function

import logging

from pytest_localstack.hookspecs import pytest_localstack_hookimpl

# import boto3


logger = logging.getLogger(__name__)


@pytest_localstack_hookimpl
def contribute_to_session(session):
    """Add :class:`Boto3TestResourceFactory` to :class:`LocalstackSession`."""
    logger.debug('patching session {!r}'.format(session))
    session.boto3 = Boto3TestResourceFactory(session)


class Boto3TestResourceFactory(object):
    """Create boto3 clients and resources to interact with a :class:`LocalstackSession`."""

    def __init__(self, session):
        logger.debug("Boto3TestResourceFactory.__init__")
        self.session = session
