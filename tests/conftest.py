import os
from unittest import mock

import pytest


@pytest.fixture(scope="session", autouse=True)
def patch_aws_env_vars():
    """Prevent any accidental calls to real AWS by setting these env vars."""
    with mock.patch.dict(
        "os.environ",
        **{
            **os.environ,
            **{
                "AWS_ACCESS_KEY_ID": "accesskey",
                "AWS_SECRET_ACCESS_KEY": "secretkey",
                "AWS_SESSION_TOKEN": "token",
                "AWS_DEFAULT_REGION": "us-east-1",
            },
        }
    ):
        yield
