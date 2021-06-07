"""Unit tests for pytest_localstack.utils."""
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pytest_localstack import utils


@given(
    string=st.text(),
    newline=st.sampled_from(["\n", "\r\n", "\r", "\n\r"]),
    num_newlines=st.integers(min_value=0, max_value=100),
    n=st.integers(min_value=-100, max_value=100),
)
def test_remove_newline(string, newline, num_newlines, n):
    assume(not (string.endswith("\n") or string.endswith("\r")))
    string_with_newlines = string + (newline * num_newlines)
    result = utils.remove_newline(string_with_newlines, n)
    assert result == string + (newline * (num_newlines - max(n, 0)))


def test_get_version_tuple():
    assert utils.get_version_tuple("1.2.3") == (1, 2, 3)
    with pytest.raises(ValueError):
        utils.get_version_tuple("latest")
