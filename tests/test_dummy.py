"""Dummy tests"""
import pytest_localstack


def test_dummy():
    """Dummy to make sure tests work."""
    assert pytest_localstack.__version__ == '0.1.0-dev'
