import boto3
import botocore.session

from pytest_localstack import patch


class TestPatchClients:
    """Test to ensure the patch() function actually patches AWS clients."""

    def test_botocore(self):
        localstack_url = "http://example.org"

        session = botocore.session.Session()

        # Without patch.
        s3_client = session.create_client("s3")
        assert s3_client._endpoint.host != localstack_url

        # With patch.
        with patch.aws_clients(localstack_url):
            s3_client = session.create_client("s3")
            assert s3_client._endpoint.host == localstack_url

        # With patch removed.
        s3_client = session.create_client("s3")
        assert s3_client._endpoint.host != localstack_url

    def test_boto3_client(self):
        localstack_url = "http://example.org"

        # Without patch.
        s3_client = boto3.client("s3")
        assert s3_client._endpoint.host != localstack_url

        # With patch.
        with patch.aws_clients(localstack_url):
            s3_client = boto3.client("s3")
            assert s3_client._endpoint.host == localstack_url

        # With patch removed.
        s3_client = boto3.client("s3")
        assert s3_client._endpoint.host != localstack_url

    def test_boto3_resource(self):
        localstack_url = "http://example.org"

        # Without patch.
        s3_resource = boto3.resource("s3")
        assert s3_resource.meta.client._endpoint.host != localstack_url

        # With patch.
        with patch.aws_clients(localstack_url):
            s3_resource = boto3.resource("s3")
            assert s3_resource.meta.client._endpoint.host == localstack_url

        # With patch removed.
        s3_resource = boto3.resource("s3")
        assert s3_resource.meta.client._endpoint.host != localstack_url
