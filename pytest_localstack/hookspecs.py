"""pytest-localstack hook specs.

.. seealso:: :mod:`~pytest_localstack.plugin`

"""
import pluggy

pytest_localstack_hookspec = pluggy.HookspecMarker("pytest-localstack")
pytest_localstack_hookimpl = pluggy.HookimplMarker("pytest-localstack")


@pytest_localstack_hookspec(historic=True)
def contribute_to_module(pytest_localstack):
    """Hook to add additional functionality to :mod:`pytest_localstack`.

    Primarially used to add fixture factories at a top level.
    """


@pytest_localstack_hookspec
def contribute_to_session(session):
    """Hook to add additional functionality to :class:`LocalstackSession`.

    Primarially used to add test resource factories to sessions.
    See :mod:`pytest_localstack.contrib.botocore` for an example of that.
    """


@pytest_localstack_hookspec
def session_starting(session):
    """Hook fired when :class:`LocalstackSession` is starting."""


@pytest_localstack_hookspec
def session_started(session):
    """Hook fired when :class:`LocalstackSession` has started."""


@pytest_localstack_hookspec
def session_stopping(session):
    """Hook fired when :class:`LocalstackSession` is stopping."""


@pytest_localstack_hookspec
def session_stopped(session):
    """Hook fired when :class:`LocalstackSession` has stopped."""
