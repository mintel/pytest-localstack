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

pytest-localstack is a plugin for pytest_ to AWS_ integration tests via a
Localstack_ Docker container.

.. _pytest: http://docs.pytest.org/
.. _AWS: https://aws.amazon.com/
.. _Localstack: https://github.com/localstack/localstack


Requirements
------------

* Docker

Quick Start
-----------

.. code-block:: bash

    $ pip install pytest-localstack


.. code-block:: python

    import boto3

    import pytest_localstack

    localstack = pytest_localstack.patch_fixture(
        services=["s3"],  # Limit to the AWS services you need.
        scope='module',  # Use the same Localstack container for all tests in this module.
        autouse=True,  # Automatically use this fixture in tests.
    )

    def test_s3_bucket_creation():
        s3 = boto3.resource('s3')  # Botocore, boto3, etc will be patched to use Localstack
        assert len(list(s3.buckets.all())) == 0
        bucket = s3.Bucket('foobar')
        bucket.create()
        assert len(list(s3.buckets.all())) == 1


.. code-block:: bash

    $ pytest


TODO
----

* Break Docker container running out of LocalstackSession.
* Make botocore patching more comprehensible.
* Add common test resource fixture factories i.e. S3 buckets, SQS queues, SNS topics, etc.
* Allow non-local Docker containers.
