"""Copy objects from one S3 bucket to another."""

import optparse

import boto3

s3 = boto3.resource("s3")


def sync_buckets(src_bucket, dest_bucket):
    """Sync objects from one AWS S3 bucket to another.

    Args:
        src_bucket (boto3 Bucket): Objects will be copied from this bucket
            to *dest_bucket*.
        dest_bucket (boto3 Bucket): Objects will be copied here from *src_bucket*.

    Returns:
        int: Count of objects copied between buckets.

    """
    count = 0
    for src_obj in src_bucket.objects.all():
        response = src_obj.get()
        dest_bucket.put_object(Key=src_obj.key, Body=response["Body"].read())
        count += 1
    return count


def sync_buckets_by_name(src_bucket_name, dest_bucket_name):
    """Sync objects from one AWS S3 bucket to another by name."""
    src_bucket = s3.Bucket(src_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)
    return sync_buckets(src_bucket, dest_bucket)


def main():
    parser = optparse.OptionParser(
        description="Copy objects from one S3 bucket to another.",
        usage="usage: %prog [options] src_bucket dest_bucket",
    )
    options, args = parser.parse_args()
    src_bucket, dest_bucket = args
    sync_buckets_by_name(src_bucket, dest_bucket)


if __name__ == "__main__":
    main()
