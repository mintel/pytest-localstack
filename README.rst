pytest-localstack
=================

.. image:: https://travis-ci.org/mintel/pytest-localstack.svg?branch=master
    :target: https://travis-ci.org/mintel/pytest-localstack

.. image:: https://img.shields.io/codecov/c/github/mintel/pytest-localstack.svg
    :target: https://codecov.io/gh/mintel/pytest-localstack

.. image:: https://img.shields.io/github/license/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/blob/master/LICENSE

.. image:: https://img.shields.io/github/issues/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/issues

.. image:: https://img.shields.io/github/forks/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/network

.. image:: https://img.shields.io/github/stars/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/stargazers

Pytest plugin for `AWS <https://aws.amazon.com/>`_ integration tests via a
`Localstasck <https://github.com/localstack/localstack>`_ Docker container.


Features
--------

* Provides Pytest fixtures that will automatically run Localstack as a Docker container.
* Patch botocore so that botocore and boto3 will use Localstack.


Getting Started
---------------

.. code-block:: bash
    pip install pytest-localstack

Patch botocore/boto3 to use a Localstack container.

.. code-block:: python
    # file: test_s3_bucket_creation.py
    import boto3

    import pytest_localstack


    # Botocore, boto3, etc will be patched to use
    # Localstack for the duration of any test
    # that includes this fixture.
    # Setting the `services` and `scope` arguments can dramatically decrease test time/resource usage.
    localstack = pytest_localstack.patch_fixture(
        services=["s3"],  # Limit to the AWS services you need.
        scope='module',  # Use the same Localstack container for all tests in this module.
        autouse=True,  # Automatically use this fixture in tests.
    )

    def test_s3_bucket_creation():
        s3 = boto3.resource('s3')  # Will use Localstack
        assert len(list(s3.buckets.all())) == 0
        bucket = s3.Bucket('foobar')
        bucket.create()
        assert len(list(s3.buckets.all())) == 1

Use Localstack without patching botocore/boto3.

.. code-block:: python
    # file: test_sync_buckets.py
    import boto3

    import pytest_localstack


    # Create a Localstack session fixture.
    # The LocalstackSession object returned by this fixture contains
    # factories for botocore/boto3 clients that will use
    # the Localstack container.
    # This is useful for simulating multiple AWS accounts.
    localstack_1 = pytest_localstack.session_fixture()
    localstack_2 = pytest_localstack.session_fixture()


    def test_sync_buckets(localstack_1, localstack_2):
        s3_1 = localstack_1.boto3.resource('s3')
        s3_2 = localstack_2.boto3.resource('s3')

        src_bucket = s3_1.Bucket('src-bucket')
        src_bucket.create()
        src_object = src_bucket.Object('foobar')
        src_object.put(Body=b'Hello world!')

        dest_bucket = s3_2.Bucket('dest-bucket')
        dest_bucket.create()

        sync_buckets(src_bucket, dest_bucket)

        response = dest_bucket.get_object('foobar')
        assert response['Body'].read() == b'Hello world!'


Roadmap
-------

* Break Docker container running out of LocalstackSession.
* Make botocore patching more comprehensible.
* Add common test resource fixture factories i.e. S3 buckets, SQS queues, SNS topics, etc.
