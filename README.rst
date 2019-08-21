pytest-localstack
=================

.. image:: https://img.shields.io/pypi/v/pytest-localstack.svg
    :alt: PyPI
    :target: https://pypi.org/project/pytest-localstack/

.. image:: https://img.shields.io/travis/mintel/pytest-localstack/master.svg
    :alt: Travis-CI
    :target: https://travis-ci.org/mintel/pytest-localstack

.. image:: https://img.shields.io/codecov/c/github/mintel/pytest-localstack.svg
    :alt: Codecov
    :target: https://codecov.io/gh/mintel/pytest-localstack

.. image:: https://img.shields.io/github/license/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/blob/master/LICENSE

.. image:: https://img.shields.io/github/issues/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/issues

.. image:: https://img.shields.io/github/forks/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/network

.. image:: https://img.shields.io/github/stars/mintel/pytest-localstack.svg
    :target: https://github.com/mintel/pytest-localstack/stargazers

pytest-localstack is a plugin for pytest_ to create AWS_ integration tests
via a Localstack_ Docker container.

`Read The Docs`_

**Requires:**

- pytest >= 3.3.0
- Docker

Tested against Python >= 3.6.

.. _pytest: http://docs.pytest.org/
.. _AWS: https://aws.amazon.com/
.. _Localstack: https://github.com/localstack/localstack
.. _Read the Docs: https://pytest-localstack.readthedocs.io/


Features
--------
* Create `pytest fixtures`_ that start and stop a Localstack container.
* Temporarily patch botocore to redirect botocore/boto3 API calls to Localstack container.
* Plugin system to easily extend supports to other AWS client libraries such as aiobotocore_.

.. _pytest fixtures: https://docs.pytest.org/en/stable/fixture.html

Example
-------
.. code-block:: python

    import boto3
    import pytest_localstack

    localstack = pytest_localstack.patch_fixture(
        services=["s3"],  # Limit to the AWS services you need.
        scope='module',  # Use the same Localstack container for all tests in this module.
        autouse=True,  # Automatically use this fixture in tests.
    )

    def test_s3_bucket_creation():
        s3 = boto3.resource('s3')  # Botocore/boto3 will be patched to use Localstack
        assert len(list(s3.buckets.all())) == 0
        bucket = s3.Bucket('foobar')
        bucket.create()
        assert len(list(s3.buckets.all())) == 1

Services
--------
* apigateway
* cloudformation
* cloudwatch
* dynamodb
* dynamodbstreams
* ec2
* es
* firehose
* iam
* kinesis
* lambda
* logs
* redshift
* route53
* s3
* secretsmanager
* ses
* sns
* sqs
* ssm
* stepfunctions
* sts

Installation
------------
.. code-block:: bash

    $ pip install pytest-localstack


TODO
----

* More detailed docs.
* Break Docker container running out of LocalstackSession.
* Make botocore patching more comprehensible.
* Add common test resource fixture factories i.e. S3 buckets, SQS queues, SNS topics, etc.
* Test this works for non-localhost Docker containers.
* Add other client libraries such as aiobotocore_.

.. _aiobotocore: https://github.com/aio-libs/aiobotocore
