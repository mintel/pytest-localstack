"""Handle compatibility issues between Python 2 and Python 3."""

import six

if six.PY3:
    from unittest import mock
else:
    import mock  # noqa
