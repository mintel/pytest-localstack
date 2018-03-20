import boto3
import pytest_localstack

from sync_buckets import sync_buckets

patch = pytest_localstack.patch_fixture(services=["s3"])
localstack_1 = pytest_localstack.session_fixture()
localstack_2 = pytest_localstack.session_fixture()


def test_sync_buckets_patch(patch):
    s3 = boto3.resource('s3')
    src_bucket = s3.Bucket('src-bucket')
    src_bucket.create()
    dest_bucket = s3.Bucket('dest-bucket')
    dest_bucket.create()

    src_bucket.put_object(Key='test', Body=b'foobar')

    result = sync_buckets(src_bucket, dest_bucket)
    assert result == 1

    
    assert len(list(dest_bucket.objects.all())) == 1

    response = dest_bucket.Object('test').get()
    data = response['Body'].read()
    assert data == b'foobar'


def test_sync_buckets_between_accounts(localstack_1, localstack_2):
    src_s3 = localstack_1.boto3.resource('s3')
    src_bucket = src_s3.Bucket('src-bucket')
    src_bucket.create()

    dest_s3 = localstack_2.boto3.resource('s3')
    dest_bucket = dest_s3.Bucket('dest-bucket')
    dest_bucket.create()

    src_bucket.put_object(Key='test', Body=b'foobar')

    result = sync_buckets(src_bucket, dest_bucket)
    assert result == 1

    assert len(list(dest_bucket.objects.all())) == 1

    response = dest_bucket.Object('test').get()
    data = response['Body'].read()
    assert data == b'foobar'

