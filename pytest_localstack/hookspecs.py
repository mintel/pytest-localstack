"""
Much like `pytest <https://pytest.readthedocs.io/en/latest/writing_plugins.html>`_,
itself, pytest-localstack uses `pluggy <https://github.com/pytest-dev/pluggy>`_
to implement a plugin system. These plugins can be used to add additional
functionality to pytest-localstack and to trigger callbacks when the
Localstack container is started and stopped.

"""
import pluggy


pytest_localstack_hookspec = pluggy.HookspecMarker("pytest-localstack")
pytest_localstack_hookimpl = pluggy.HookimplMarker("pytest-localstack")


@pytest_localstack_hookspec(historic=True)
def contribute_to_module(pytest_localstack):
    """
    Hook to add additional functionality to the :mod:`pytest_localstack`
    module.

    Primarily used to add importable fixture factories at a top level.
    """


@pytest_localstack_hookspec
def contribute_to_session(session):
    """Hook to add additional functionality to :class:`LocalstackSession`.

    Primarily used to add test resource factories to sessions.
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
