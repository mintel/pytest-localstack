import botocore
import botocore.session

import pytest
from tests import utils as test_utils

import pytest_localstack
from pytest_localstack import constants, exceptions, plugin
from pytest_localstack.contrib import botocore as localstack_botocore


def test_patch_fixture_contributed_to_module():
    assert pytest_localstack.patch_fixture is localstack_botocore.patch_fixture


def test_session_contribution():
    dummy_session = type("DummySession", (object,), {})()
    plugin.manager.hook.contribute_to_session(session=dummy_session)
    assert isinstance(
        dummy_session.botocore, localstack_botocore.BotocoreTestResourceFactory
    )


def test_create_credential_resolver():
    """Test pytest_localstack.botocore.create_credential_resolver."""
    resolver = localstack_botocore.create_credential_resolver()
    assert isinstance(resolver, botocore.credentials.CredentialResolver)


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("region_name", test_utils.AWS_REGIONS)
@pytest.mark.parametrize("not_region_name", test_utils.AWS_REGIONS)
@pytest.mark.parametrize(
    "service_alias",
    sorted(
        list(constants.SERVICE_ALIASES.keys()) + list(constants.SERVICE_PORTS.keys())
    ),
)
def test_LocalstackEndpointResolver(
    region_name, not_region_name, service_alias, make_test_session
):
    """Test pytest_localstack.botocore.LocalstackEndpointResolver."""
    if region_name == not_region_name:
        pytest.skip("Should not be equal.")
    service_name = constants.SERVICE_ALIASES.get(service_alias, service_alias)
    localstack = make_test_session(region_name=region_name, use_ssl=False)

    # Is the correct type.
    resolver = localstack.botocore.session().get_component("endpoint_resolver")
    assert isinstance(resolver, localstack_botocore.LocalstackEndpointResolver)
    assert isinstance(resolver, botocore.regions.EndpointResolver)

    # Only supports 'aws' partition.
    result = resolver.get_available_partitions()
    assert result == ["aws"]
    with pytest.raises(exceptions.UnsupportedPartitionError):
        resolver.get_available_endpoints(service_alias, partition_name="aws-cn")

    # Can only return the region LocalstackSession was configure with or aws-global.
    result = resolver.get_available_endpoints(service_alias)
    result = set(result)
    result.discard(localstack.region_name)
    result.discard("aws-global")
    assert not result

    if hasattr(localstack, "_container"):
        # Can't construct endpoints until the container is started.
        with pytest.raises(exceptions.ContainerNotStartedError):
            result = resolver.construct_endpoint(service_alias)

    with localstack:  # Start container.
        with pytest.raises(exceptions.RegionError):
            # Can only get endpoints for the region LocalstackSession
            # was configured with.
            result = resolver.construct_endpoint(
                service_alias, region_name=not_region_name
            )

        result = resolver.construct_endpoint(service_alias)
        assert result["partition"] == "aws"
        assert result["endpointName"] in (localstack.region_name, "aws-global")
        assert (
            result["hostname"] == "127.0.0.1:%i" % constants.SERVICE_PORTS[service_name]
        )
        assert result["protocols"] == ["http"]


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("region_name", test_utils.AWS_REGIONS)
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_session(region_name, service_name, make_test_session):
    """Test Session creation."""
    localstack = make_test_session(region_name=region_name)

    ls_session = localstack.botocore.session()
    assert isinstance(ls_session, localstack_botocore.Session)

    if hasattr(localstack, "_container"):
        with pytest.raises(exceptions.ContainerNotStartedError):
            # Can't create clients until the container is started,
            # because the client needs to know what port its
            # target service is running on.
            bc_client = ls_session.create_client(service_name, localstack.region_name)

    with localstack:  # Start container.
        bc_client = ls_session.create_client(service_name, localstack.region_name)
        assert isinstance(bc_client, botocore.client.BaseClient)
        assert "127.0.0.1" in bc_client._endpoint.host


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("region_name", test_utils.AWS_REGIONS)
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_client(region_name, service_name, make_test_session):
    """Test Client creation."""
    localstack = make_test_session(region_name=region_name)

    if hasattr(localstack, "_container"):
        with pytest.raises(exceptions.ContainerNotStartedError):
            bc_client = localstack.botocore.client(service_name, localstack.region_name)

    with localstack:  # Start container.
        bc_client = localstack.botocore.client(service_name, localstack.region_name)
        assert isinstance(bc_client, botocore.client.BaseClient)
        assert "127.0.0.1" in bc_client._endpoint.host


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("region_name", test_utils.AWS_REGIONS)
def test_default_session(region_name, make_test_session):
    """Test default session."""
    localstack = make_test_session(region_name=region_name)
    session_1 = localstack.botocore.default_session
    session_2 = localstack.botocore.default_session
    assert session_1 is session_2


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
@pytest.mark.parametrize("region_name", test_utils.AWS_REGIONS)
@pytest.mark.parametrize("service_name", sorted(constants.SERVICE_PORTS.keys()))
def test_patch(region_name, service_name, make_test_session):
    """Test patching."""
    localstack = make_test_session(region_name=region_name)

    with localstack:
        # Haven't patched yet.
        # A regular botocore client should point to AWS right now.
        original_bc_session = botocore.session.get_session()
        original_bc_client = original_bc_session.create_client(
            service_name, localstack.region_name
        )
        assert "127.0.0.1" not in original_bc_client._endpoint.host

        with localstack.botocore.patch_botocore():
            # Original client should now point to Localstack
            assert "127.0.0.1" in original_bc_client._endpoint.host

            # Original session should create Localstack clients
            ls_client = original_bc_session.create_client(
                service_name, localstack.region_name
            )
            assert "127.0.0.1" in ls_client._endpoint.host

        # Original client back to AWS
        assert "127.0.0.1" not in original_bc_client._endpoint.host

        # Original session should create AWS clients
        bc_client = original_bc_session.create_client(
            service_name, localstack.region_name
        )
        assert "127.0.0.1" not in bc_client._endpoint.host

        # Localstack client create while patched still points to Localstack
        assert "127.0.0.1" in ls_client._endpoint.host


@pytest.mark.parametrize(
    "make_test_session",
    [test_utils.make_test_LocalstackSession, test_utils.make_test_RunningSession],
)
def test_exceptions_populated(make_test_session):
    """Patched botocore clients populated `exceptions` correctly."""
    botocore_session = botocore.session.get_session()
    botocore_client = botocore_session.create_client("s3")

    localstack = make_test_session()

    assert botocore_client._exceptions is None

    with localstack, localstack.botocore.patch_botocore():
        result = botocore_client.exceptions
        assert result is not None
        assert botocore_client._exceptions is not None

    assert botocore_client._exceptions is None
