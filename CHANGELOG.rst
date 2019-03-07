Change Log
==========

0.2.0 (2019-03-06)
------------------

- Use botocore to determine default AWS region (will us-east-1 fallback).
- Replace use of `pytest.config` with `pytest_configure()` hook.

0.1.5 (2018-08-17)
------------------

- Fix a bug involving our patched botocore Session trying to access `_internal_components` and getting `_components` instead.

0.1.4 (2018-08-03)
------------------

- Fix pinned install requirements conflict between pytest and pluggy.

0.1.3 (2018-07-17)
------------------

- Fix for botocore >= 1.10.58.

0.1.2 (2018-06-22)
------------------

- Broke out LocalstackSession into RunningSession which doesn't start localstack itself.

0.1.1 (2018-04-23)
------------------

- Fixed bug where patched botocore clients wouldn't populated the `_exceptions` attribute.

0.1.0 (2018-03-13)
------------------

- Initial release
