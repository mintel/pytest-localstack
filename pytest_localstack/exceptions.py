"""Exceptions for pytest-localstack."""


class Error(Exception):
    """Base exception for all pytest-localstack errors."""


class ContainerNotStartedError(Error):
    """Raised when :class:`~.LocalstackSession` container isn't started yet."""

    def __init__(self, session, *args, **kwargs):
        msg = f"{session!r} isn't started yet"
        super().__init__(msg, *args, **kwargs)


class ServiceError(Error):
    """Raised when a Localstack service isn't responding."""

    def __init__(self, msg=None, service_name=None, *args, **kwargs):
        if not msg:
            if service_name:
                msg = f"{service_name} isn't responding"
            else:
                msg = "Service error"
        super().__init__(msg, *args, **kwargs)


class ContainerAlreadyStartedError(Error):
    """Raised when :class:`~.LocalstackSession` container is started twice."""

    def __init__(self, session, *args, **kwargs):
        msg = f"{session!r} is already started"
        super().__init__(msg, *args, **kwargs)


class TimeoutError(Error):
    """Raised when :meth:`~.LocalstackSession.start` takes too long."""


class UnsupportedPartitionError(Error):
    """Raised when asking for an AWS partition that isn't 'aws'."""

    def __init__(self, partition_name):
        super().__init__(
            f"LocalstackEndpointResolver only supports the 'aws' partition, not '{partition_name}'"
        )


class UnsupportedLocalstackVersionError(Error):
    """Raised when"""

    def __init__(self, image):
        super().__init__(
            f"Localstack Docker image '{image}' isn't supported (must be >= v0.11.6)"
        )


class RegionError(Error):
    """Raised when asking Localstack for the wrong region.

    LocalstackSession can only pretent to be one AWS region.
    This exception is thrown when trying to access a region
    LocalstackSession isn't configured as.
    """

    def __init__(self, region_name, should_be_region):
        super().__init__(
            f"This LocalstackSession is configured for region {should_be_region}, not {region_name}"
        )
