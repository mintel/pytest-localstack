"""Unit tests for pytest_localstack.utils."""
import os

import pytest
from hypothesis import (
    given,
    strategies as st,
)

from pytest_localstack import (
    compat,
    utils,
)


def _get_env_var(name):
    return os.environ.get(name) or os.environ.get(name.upper(), '')


@given(
    test_environ=st.fixed_dictionaries({
        'http_proxy': st.sampled_from(['', 'http://proxy:3128']),
        'https_proxy': st.sampled_from(['', 'http://proxy:3128']),
        'HTTP_PROXY': st.sampled_from(['', 'http://proxy:3128']),
        'HTTPS_PROXY': st.sampled_from(['', 'http://proxy:3128']),
        'no_proxy': st.sampled_from(['', 'localhost,127.0.0.1', 'localhost', 'foobar']),
        'NO_PROXY': st.sampled_from(['', 'localhost,127.0.0.1', 'localhost', 'foobar']),
    })
)
def test_check_no_proxy(test_environ):
    """Test pytest_localstack.utils.check_no_proxy."""
    with compat.mock.patch.dict(os.environ):
        # mock.patch.dict can't delete keys.
        # Patch os.environ manually.
        for key, value in test_environ.items():
            if value:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

        has_http_proxy = bool(_get_env_var('http_proxy'))
        has_https_proxy = bool(_get_env_var('https_proxy'))
        good_no_proxy = '127.0.0.1' in _get_env_var('no_proxy')

        if has_http_proxy or has_https_proxy:
            if good_no_proxy:
                utils.check_no_proxy()
            else:
                with pytest.raises(UserWarning):
                    utils.check_no_proxy()
        else:
            utils.check_no_proxy()
