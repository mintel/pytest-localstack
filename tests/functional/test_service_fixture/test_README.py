"""Test examples from the README."""
import pytest_localstack

s3_service_1 = pytest_localstack.session_fixture(services=["s3"])
s3_service_2 = pytest_localstack.session_fixture(services=["s3"])


def test_sync_buckets(s3_service_1, s3_service_2):
    """Test using multple sessions in one test."""
    s3_1 = s3_service_1.boto3.resource("s3")
    s3_2 = s3_service_2.boto3.resource("s3")

    src_bucket = s3_1.Bucket("src-bucket")
    src_bucket.create()
    src_object = src_bucket.Object("foobar")
    src_object.put(Body=b"Hello world!")

    dest_bucket = s3_2.Bucket("dest-bucket")
    dest_bucket.create()

    _sync_buckets(src_bucket, dest_bucket)

    response = dest_bucket.Object("foobar").get()
    assert response["Body"].read() == b"Hello world!"


def _sync_buckets(src_bucket, dest_bucket):
    for src_obj in src_bucket.objects.all():
        dest_obj = dest_bucket.Object(src_obj.key)
        response = src_obj.get()
        kwargs = {"Body": response["Body"].read()}
        for key in [
            "CacheControl",
            "ContentDisposition",
            "ContentEncoding",
            "ContentType",
            "Expires",
            "WebsiteRedirectLocation",
            "ServerSideEncryption",
            "Metadata",
            "SSECustomerAlgorithm",
            "SSECustomerKeyMD5",
            "SSEKMSKeyId",
            "StorageClass",
        ]:
            if key in response:
                kwargs[key] = response[key]
        dest_obj.put(**kwargs)
