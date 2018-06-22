"""Test all services accessible for pytest_localstack.session_fixture."""
import pytest_localstack

localstack = pytest_localstack.session_fixture(scope="module", autouse=True)


def _assert_key_isinstance(result, key, type):
    assert key in result
    assert isinstance(result[key], type)


class TestBotocore(object):
    """Test service accessibility via botocore."""

    def test_apigateway_available(self, localstack):
        client = localstack.botocore.client("apigateway")
        result = client.get_rest_apis()
        assert result["items"] == []

    def test_cloudformation_available(self, localstack):
        client = localstack.botocore.client("cloudformation")
        result = client.list_stacks(
            StackStatusFilter=[
                "CREATE_IN_PROGRESS",
                "CREATE_FAILED",
                "CREATE_COMPLETE",
                "ROLLBACK_IN_PROGRESS",
                "ROLLBACK_FAILED",
                "ROLLBACK_COMPLETE",
                "DELETE_IN_PROGRESS",
                "DELETE_FAILED",
                "DELETE_COMPLETE",
                "UPDATE_IN_PROGRESS",
                "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                "UPDATE_COMPLETE",
                "UPDATE_ROLLBACK_IN_PROGRESS",
                "UPDATE_ROLLBACK_FAILED",
                "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                "UPDATE_ROLLBACK_COMPLETE",
                "REVIEW_IN_PROGRESS",
            ]
        )
        _assert_key_isinstance(result, "StackSummaries", list)

    def test_cloudwatch_available(self, localstack):
        client = localstack.botocore.client("cloudwatch")
        result = client.list_metrics()
        _assert_key_isinstance(result, "Metrics", list)

    def test_dynamodb_available(self, localstack):
        client = localstack.botocore.client("dynamodb")
        result = client.list_tables()
        _assert_key_isinstance(result, "TableNames", list)

    def test_dynamodbstreams_available(self, localstack):
        client = localstack.botocore.client("dynamodbstreams")
        result = client.list_streams()
        _assert_key_isinstance(result, "Streams", list)

    def test_es_available(self, localstack):
        client = localstack.botocore.client("es")
        result = client.list_domain_names()
        _assert_key_isinstance(result, "DomainNames", list)

    def test_firehose_available(self, localstack):
        client = localstack.botocore.client("firehose")
        result = client.list_delivery_streams()
        _assert_key_isinstance(result, "DeliveryStreamNames", list)

    def test_kinesis_available(self, localstack):
        client = localstack.botocore.client("kinesis")
        result = client.list_streams()
        _assert_key_isinstance(result, "StreamNames", list)

    def test_lambda_available(self, localstack):
        client = localstack.botocore.client("lambda")
        result = client.list_functions()
        _assert_key_isinstance(result, "Functions", list)

    def test_redshift_available(self, localstack):
        client = localstack.botocore.client("redshift")
        result = client.describe_clusters()
        _assert_key_isinstance(result, "Clusters", list)

    def test_route53_available(self, localstack):
        client = localstack.botocore.client("route53")
        result = client.list_hosted_zones()
        _assert_key_isinstance(result, "HostedZones", list)

    def test_s3_available(self, localstack):
        client = localstack.botocore.client("s3")
        result = client.list_buckets()
        _assert_key_isinstance(result, "Buckets", list)

    def test_ses_available(self, localstack):
        client = localstack.botocore.client("ses")
        result = client.list_identities()
        _assert_key_isinstance(result, "Identities", list)

    def test_sns_available(self, localstack):
        client = localstack.botocore.client("sns")
        result = client.list_topics()
        _assert_key_isinstance(result, "Topics", list)

    def test_sqs_available(self, localstack):
        client = localstack.botocore.client("sqs")
        result = client.list_queues()
        assert "ResponseMetadata" in result
        assert "HTTPStatusCode" in result["ResponseMetadata"]
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200


class TestBoto3Clients(object):
    """Test service accessibility via boto3 clients."""

    def test_apigateway_available(self, localstack):
        client = localstack.boto3.client("apigateway")
        result = client.get_rest_apis()
        assert result["items"] == []

    def test_cloudformation_available(self, localstack):
        client = localstack.boto3.client("cloudformation")
        result = client.list_stacks(
            StackStatusFilter=[
                "CREATE_IN_PROGRESS",
                "CREATE_FAILED",
                "CREATE_COMPLETE",
                "ROLLBACK_IN_PROGRESS",
                "ROLLBACK_FAILED",
                "ROLLBACK_COMPLETE",
                "DELETE_IN_PROGRESS",
                "DELETE_FAILED",
                "DELETE_COMPLETE",
                "UPDATE_IN_PROGRESS",
                "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                "UPDATE_COMPLETE",
                "UPDATE_ROLLBACK_IN_PROGRESS",
                "UPDATE_ROLLBACK_FAILED",
                "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                "UPDATE_ROLLBACK_COMPLETE",
                "REVIEW_IN_PROGRESS",
            ]
        )
        _assert_key_isinstance(result, "StackSummaries", list)

    def test_cloudwatch_available(self, localstack):
        client = localstack.boto3.client("cloudwatch")
        result = client.list_metrics()
        _assert_key_isinstance(result, "Metrics", list)

    def test_dynamodb_available(self, localstack):
        client = localstack.boto3.client("dynamodb")
        result = client.list_tables()
        _assert_key_isinstance(result, "TableNames", list)

    def test_dynamodbstreams_available(self, localstack):
        client = localstack.boto3.client("dynamodbstreams")
        result = client.list_streams()
        _assert_key_isinstance(result, "Streams", list)

    def test_es_available(self, localstack):
        client = localstack.boto3.client("es")
        result = client.list_domain_names()
        _assert_key_isinstance(result, "DomainNames", list)

    def test_firehose_available(self, localstack):
        client = localstack.boto3.client("firehose")
        result = client.list_delivery_streams()
        _assert_key_isinstance(result, "DeliveryStreamNames", list)

    def test_kinesis_available(self, localstack):
        client = localstack.boto3.client("kinesis")
        result = client.list_streams()
        _assert_key_isinstance(result, "StreamNames", list)

    def test_lambda_available(self, localstack):
        client = localstack.boto3.client("lambda")
        result = client.list_functions()
        _assert_key_isinstance(result, "Functions", list)

    def test_redshift_available(self, localstack):
        client = localstack.boto3.client("redshift")
        result = client.describe_clusters()
        _assert_key_isinstance(result, "Clusters", list)

    def test_route53_available(self, localstack):
        client = localstack.boto3.client("route53")
        result = client.list_hosted_zones()
        _assert_key_isinstance(result, "HostedZones", list)

    def test_s3_available(self, localstack):
        client = localstack.boto3.client("s3")
        result = client.list_buckets()
        _assert_key_isinstance(result, "Buckets", list)

    def test_ses_available(self, localstack):
        client = localstack.boto3.client("ses")
        result = client.list_identities()
        _assert_key_isinstance(result, "Identities", list)

    def test_sns_available(self, localstack):
        client = localstack.boto3.client("sns")
        result = client.list_topics()
        _assert_key_isinstance(result, "Topics", list)

    def test_sqs_available(self, localstack):
        client = localstack.boto3.client("sqs")
        result = client.list_queues()
        assert "ResponseMetadata" in result
        assert "HTTPStatusCode" in result["ResponseMetadata"]
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200


class TestBoto3Resources(object):
    """Test service accessibility via boto3 resources."""

    def test_cloudformation_available(self, localstack):
        cloudformation = localstack.boto3.resource("cloudformation")
        assert isinstance(list(cloudformation.stacks.all()), list)

    def test_cloudwatch_available(self, localstack):
        cloudwatch = localstack.boto3.resource("cloudwatch")
        assert isinstance(list(cloudwatch.alarms.all()), list)

    def test_dynamodb_available(self, localstack):
        dynamodb = localstack.boto3.resource("dynamodb")
        assert isinstance(list(dynamodb.tables.all()), list)

    def test_s3_available(self, localstack):
        s3 = localstack.boto3.resource("s3")
        assert isinstance(list(s3.buckets.all()), list)

    def test_sns_available(self, localstack):
        sns = localstack.boto3.resource("sns")
        assert isinstance(list(sns.topics.all()), list)

    def test_sqs_available(self, localstack):
        sqs = localstack.boto3.resource("sqs")
        assert isinstance(list(sqs.queues.all()), list)
