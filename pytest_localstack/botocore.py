"""Test resource factory for the botocore library."""
import contextlib
import functools
import inspect
import logging
import socket
import weakref
from typing import TYPE_CHECKING
from unittest import mock

import botocore
import botocore.client
import botocore.config
import botocore.credentials
import botocore.regions
import botocore.session

from pytest_localstack import constants, exceptions, utils


if TYPE_CHECKING:
    from pytest_localstack.session import RunningSession


try:
    import boto3
except ImportError:
    boto3 = None

logger = logging.getLogger(__name__)


class BotocoreTestResourceFactory:
    """Create botocore clients to interact with a :class:`.LocalstackSession`.

    Args:
        localstack_session (:class:`.LocalstackSession`):
            The session that this factory should create test resources for.

    """

    def __init__(self, localstack_session):
        logger.debug("BotocoreTestResourceFactory.__init__")
        self.localstack_session = localstack_session
        self._default_session = None

    def session(self, *args, **kwargs):
        """Create a botocore Session that will use Localstack.

        Arguments are the same as :class:`botocore.session.Session`.
        """
        return Session(self.localstack_session, *args, **kwargs)

    def client(self, service_name, *args, **kwargs):
        """Create a botocore client that will use Localstack.

        Arguments are the same as
        :meth:`botocore.session.Session.create_client`.
        """
        return self.default_session.create_client(service_name, *args, **kwargs)

    @property
    def default_session(self):
        """Return a default botocore Localstack Session.

        Most applications only need one Session.
        """
        if self._default_session is None:
            self._default_session = self.session()
        return self._default_session

    @contextlib.contextmanager
    def patch_botocore(self):
        """Context manager that will patch botocore to use Localstack.

        Since boto3 relies on botocore to perform API calls, this method
        also effectively patches boto3.
        """
        # Q: Why is this method so complicated?
        # A: Because the most common usecase is something like this::
        #
        #     >>> import boto3
        #     >>>
        #     >>> S3 = boto3.resource('s3')
        #     >>>
        #     >>> def do_stuff():
        #     >>>     bucket = S3.Bucket('foobar')
        #     >>>     bucket.create()
        #     ...
        #
        #   The `S3` resource creates a botocore Client when the module
        #   is loaded. It's hard to patch existing Client instances since
        #   there isn't a good way to find them.
        #   You must add a descriptor to the Client class
        #   that overrides specific properties of the Client instances.
        #   TODO: Could we use use `gc.get_referrers()` to find instances?
        logger.debug("enter patch")
        if boto3 is not None:
            preexisting_boto3_session = boto3.DEFAULT_SESSION

        try:
            factory = self
            patches = []

            # Step 1: patch botocore Session to use Localstack.
            attr = {}

            @property
            def localstack_session(self):
                # Simlate the 'localstack_session' attr from Session class below.
                # Patch this into the botocore Session class.
                if "localstack_session" in self.__dict__:
                    # We're patching this into the base botocore Session,
                    # but we don't want to override things for the Session
                    # subclass below.
                    return self.__dict__["localstack_session"]
                return factory.localstack_session

            @localstack_session.setter
            def localstack_session(self, value):
                if not isinstance(value, RunningSession):
                    raise TypeError(
                        f"localstack_session value is type {value.__class__.__name__}, must be a LocalstackSession"
                    )
                self.__dict__["localstack_session"] = value

            attr["localstack_session"] = localstack_session

            @property
            def _components(self):
                if isinstance(self, Session):
                    try:
                        return self.__dict__["_components"]
                    except KeyError:
                        raise AttributeError("_components")
                proxy_components = botocore.session.Session._proxy_components
                if self not in proxy_components:
                    proxy_components[self] = botocore.session.ComponentLocator()
                    self._register_components()
                return proxy_components[self]

            @_components.setter
            def _components(self, value):
                self.__dict__["_components"] = value

            @property
            def _internal_components(self):
                if isinstance(self, Session):
                    try:
                        return self.__dict__["_internal_components"]
                    except KeyError:
                        raise AttributeError("_internal_components")
                proxy_components = botocore.session.Session._proxy_components
                if self not in proxy_components:
                    proxy_components[self] = DebugComponentLocator()  # noqa
                    self._register_components()
                return proxy_components[self]

            @_internal_components.setter
            def _internal_components(self, value):
                self.__dict__["_internal_components"] = value

            attr.update(
                {
                    "_components": _components,
                    "_internal_components": _internal_components,
                    "_proxy_components": weakref.WeakKeyDictionary(),
                }
            )

            @property
            def _credentials(self):
                return self._proxy_credentials.get(self)

            @_credentials.setter
            def _credentials(self, value):
                self._proxy_credentials[self] = value

            attr.update(
                {
                    "_credentials": _credentials,
                    "_proxy_credentials": weakref.WeakKeyDictionary(),
                }
            )

            patches.append(
                mock.patch.multiple("botocore.session.Session", create=True, **attr)
            )
            patches.append(
                mock.patch.multiple(
                    botocore.session.Session,
                    _register_endpoint_resolver=utils.unbind(
                        Session._register_endpoint_resolver
                    ),
                    _register_credential_provider=utils.unbind(
                        Session._register_credential_provider
                    ),
                    create_client=utils.unbind(Session.create_client),
                )
            )

            # Step 2: Safety checks
            # Make absolutly sure we use Localstack and not AWS.
            _original_convert_to_request_dict = (
                botocore.client.BaseClient._convert_to_request_dict
            )

            @functools.wraps(_original_convert_to_request_dict)
            def _convert_to_request_dict(self, *args, **kwargs):
                request_dict = _original_convert_to_request_dict(self, *args, **kwargs)
                if not (
                    factory.localstack_session.hostname in request_dict["url"]
                    or socket.gethostname() in request_dict["url"]
                ):
                    # The URL of the request points to something other than localstack.
                    raise Exception("request dict is not patched")
                return request_dict

            patches.append(
                mock.patch(
                    "botocore.client.BaseClient._convert_to_request_dict",
                    _convert_to_request_dict,
                )
            )

            # Step 3: Patch existing clients
            # Patching botocore Session doesn't help with an existing
            # botocore Clients objects. They will have already been created with
            # endpoints aimed at AWS. We need to patch botocore.client.BaseClient
            # to temporarially act like a Localstack.
            original_init = botocore.client.BaseClient.__init__

            @functools.wraps(original_init)
            def new_init(self, *args, **kwargs):
                # Every client created during the patch is a Localstack client.
                # Set this flag so that the proxy_client_attr() stuff below
                # won't break during original_init().
                self._is_pytest_localstack = True
                original_init(self, *args, **kwargs)

            patches.append(
                mock.patch.multiple(botocore.client.BaseClient, __init__=new_init)
            )

            # Create a place to store proxy clients.
            patches.append(
                mock.patch(
                    "botocore.client.BaseClient._proxy_clients",
                    weakref.WeakKeyDictionary(),
                    create=True,
                )
            )

            def new_getattribute(self, key):
                if key.startswith("__"):
                    return object.__getattribute__(self, key)
                proxied_keys = [
                    "_cache",
                    "_client_config",
                    "_endpoint",
                    "_exceptions_factory",
                    "_exceptions",
                    "exceptions",
                    "_loader",
                    "_request_signer",
                    "_response_parser",
                    "_serializer",
                    "meta",
                ]
                __dict__ = object.__getattribute__(self, "__dict__")
                if (
                    __dict__.get("_is_pytest_localstack", False)
                    or key not in proxied_keys
                ):
                    # Don't proxy clients that are already Localstack clients
                    return object.__getattribute__(self, key)
                if self not in botocore.client.BaseClient._proxy_clients:
                    try:
                        meta = __dict__["meta"]
                    except KeyError:
                        raise AttributeError("meta")
                    proxy = factory.default_session.create_client(
                        meta.service_model.service_name,
                        # config=config,
                        config=__dict__["_client_config"],
                    )
                    botocore.client.BaseClient._proxy_clients[self] = proxy
                return object.__getattribute__(
                    botocore.client.BaseClient._proxy_clients[self], key
                )

            patches.append(
                mock.patch(
                    "botocore.client.BaseClient.__getattribute__",
                    new_getattribute,
                    create=True,
                )
            )

            # STS is sneaky and even after patching the endpoint it has a final custom check
            # to see whether it should override with the global endpoint url... patch that too

            patches.append(
                mock.patch(
                    "botocore.args.ClientArgsCreator._should_set_global_sts_endpoint",
                    lambda *args, **kwargs: False,
                )
            )

            with utils.nested(*patches):
                yield
        finally:
            logger.debug("exit patch")
            if boto3 is not None:
                boto3.DEFAULT_SESSION = preexisting_boto3_session


# Grab a reference here to avoid breaking things during patching.
_original_create_client = utils.unbind(botocore.session.Session.create_client)


class Session(botocore.session.Session):
    """A botocore Session subclass that talks to Localstack."""

    def __init__(self, localstack_session, *args, **kwargs):
        self.localstack_session = localstack_session
        super().__init__(*args, **kwargs)

    def _register_endpoint_resolver(self):
        def create_default_resolver():
            loader = self.get_component("data_loader")
            endpoints = loader.load_data("endpoints")
            return LocalstackEndpointResolver(self.localstack_session, endpoints)

        if constants.BOTOCORE_VERSION >= (1, 10, 58):
            self._internal_components.lazy_register_component(
                "endpoint_resolver", create_default_resolver
            )
        else:
            self._components.lazy_register_component(
                "endpoint_resolver", create_default_resolver
            )

    def _register_credential_provider(self):
        self._components.lazy_register_component(
            "credential_provider", create_credential_resolver
        )

    def create_client(self, *args, **kwargs):
        """Create a botocore client."""
        # Localstack doesn't use the virtual host addressing style.
        config = botocore.config.Config(s3={"addressing_style": "path"})
        callargs = inspect.getcallargs(_original_create_client, self, *args, **kwargs)
        if callargs.get("config"):
            config = callargs["config"].merge(config)
        callargs["config"] = config
        with mock.patch(
            "botocore.args.ClientArgsCreator._should_set_global_sts_endpoint",
            lambda *args, **kwargs: False,
        ):
            client = _original_create_client(**callargs)
        client._is_pytest_localstack = True
        return client


def create_credential_resolver():
    """Create a credentials resolver for Localstack."""
    env_provider = botocore.credentials.EnvProvider()
    default = DefaultCredentialProvider()
    resolver = botocore.credentials.CredentialResolver(
        providers=[env_provider, default]
    )
    return resolver


class DefaultCredentialProvider(botocore.credentials.CredentialProvider):
    """Provide some default credentials for Localstack clients."""

    METHOD = "localstack-default"

    def load(self):
        """Return credentials."""
        return botocore.credentials.Credentials(
            access_key=constants.DEFAULT_AWS_ACCESS_KEY_ID,
            secret_key=constants.DEFAULT_AWS_SECRET_ACCESS_KEY,
            token=constants.DEFAULT_AWS_SESSION_TOKEN,
            method=self.METHOD,
        )


class LocalstackEndpointResolver(botocore.regions.EndpointResolver):
    """Resolve AWS service endpoints based on a LocalstackSession."""

    def __init__(self, localstack_session, endpoints):
        self.localstack_session = localstack_session
        super().__init__(endpoints)

    @property
    def valid_regions(self):
        """Return a list of regions we can resolve endpoints for."""
        return set([self.localstack_session.region_name, "aws-global"])

    def get_available_partitions(self):
        """List the partitions available to the endpoint resolver."""
        return ["aws"]

    def get_available_endpoints(
        self, service_name, partition_name="aws", allow_non_regional=False
    ):
        """List the endpoint names of a particular partition."""
        if partition_name != "aws":
            raise exceptions.UnsupportedPartitionError(partition_name)
        result = []
        for partition in self._endpoint_data["partitions"]:
            if partition["partition"] != "aws":
                continue
            services = partition["services"]
            if service_name not in services:
                continue
            for endpoint_name in services[service_name]["endpoints"]:
                if allow_non_regional or endpoint_name in self.valid_regions:
                    result.append(endpoint_name)
        return result

    def construct_endpoint(self, service_name, region_name=None):
        """Resolve an endpoint for a service and region combination."""
        if region_name is None:
            region_name = self.localstack_session.region_name
        elif region_name not in self.valid_regions:
            raise exceptions.RegionError(
                region_name, self.localstack_session.region_name
            )
        for partition in self._endpoint_data["partitions"]:
            if partition["partition"] != "aws":
                continue
            result = self._endpoint_for_partition(partition, service_name, region_name)
            if result:
                result["hostname"] = self.localstack_session.service_hostname(
                    service_name
                )
                result["protocols"] = (
                    result["protocols"] if self.localstack_session.use_ssl else ["http"]
                )
                if not self.localstack_session.use_ssl:
                    result.pop("sslCommonName", None)
                result["dnsSuffix"] = self.localstack_session.hostname
                return result
