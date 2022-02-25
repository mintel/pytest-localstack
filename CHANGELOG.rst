Change Log
==========

Unreleased
----------

- Drop support for Python < 3.6.
- Switch to using the new single port for localstack >= 0.11.0.
- Fix bug in STS client endpoint patching.
- Update patching to be compatible with newer botocore versions.

0.4.1 (2019-08-22)
------------------

- Raise TimeoutErrors when services fail to start from any causing exception.
- Use more botocore client-based service checks.

0.4.0 (2019-08-21)
------------------

- Add EC2 service.
- Add IAM service.
- Add Secret Manager service.
- Add Step Functions service.
- Add STS service.

0.3.2 (2019-08-16)
------------------

- Track/restore original boto3.DEFAULT_SESSION during patching.


0.3.1 (2019-08-13)
------------------

- Fix exclusion of tests from installed packages.

0.3.0 (2019-07-02)
------------------

- Add CloudWatch Logs service.

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
