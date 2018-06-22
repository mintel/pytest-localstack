"""Test examples from the README."""
import boto3

import pytest

import pytest_localstack

patch_s3 = pytest_localstack.patch_fixture(services=["s3"])


@pytest.mark.usefixtures("patch_s3")
def test_s3_bucket_creation():
    """Test S3 bucket creation with patch fixture."""
    s3 = boto3.resource("s3")  # Will use Localstack
    assert len(list(s3.buckets.all())) == 0
    bucket = s3.Bucket("foobar")
    bucket.create()
