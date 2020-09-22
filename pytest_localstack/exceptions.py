"""Exceptions for pytest-localstack."""


from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import pytest_localstack.session


class Error(Exception):
    """Base exception for all pytest-localstack errors."""


class ContainerNotStartedError(Error):
    """Raised when :class:`~.LocalstackSession` container isn't started yet."""

    def __init__(
        self,
        session: "pytest_localstack.session.LocalstackSession",
        *args,
    ) -> None:
        msg = "{0!r} isn't started yet".format(session)
        super(ContainerNotStartedError, self).__init__(msg, *args)


class ServiceError(Error):
    """Raised when a Localstack service isn't responding."""

    def __init__(
        self,
        msg: Optional[str] = None,
        service_name: Optional[str] = None,
        *args,
    ) -> None:
        if not msg:
            if service_name:
                msg = "{0} isn't responding".format(service_name)
            else:
                msg = "Service error"
        super(ServiceError, self).__init__(msg, *args)


class ContainerAlreadyStartedError(Error):
    """Raised when :class:`~.LocalstackSession` container is started twice."""

    def __init__(
        self, session: "pytest_localstack.session.LocalstackSession", *args
    ) -> None:
        msg = "{0!r} is already started".format(session)
        super(ContainerAlreadyStartedError, self).__init__(msg, *args)


class TimeoutError(Error):
    """Raised when :meth:`~.LocalstackSession.start` takes too long."""


class UnsupportedPartitionError(Error):
    """Raised when asking for an AWS partition that isn't 'aws'."""

    def __init__(self, partition_name: str) -> None:
        super(UnsupportedPartitionError, self).__init__(
            "LocalstackEndpointResolver only supports the 'aws' partition, "
            "not '%s'" % (partition_name,)
        )


class RegionError(Error):
    """Raised when asking Localstack for the wrong region.

    LocalstackSession can only pretent to be one AWS region.
    This exception is thrown when trying to access a region
    LocalstackSession isn't configured as.
    """

    def __init__(self, region_name: str, should_be_region: str) -> None:
        super(RegionError, self).__init__(
            "This LocalstackSession is configured for region %s, not %s"
            % (should_be_region, region_name)
        )
