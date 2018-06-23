#!/usr/bin/env python
import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

# Dependencies for this Python library.
REQUIRES = [
    "botocore>=1.4.31,!=1.4.45",
    'contextlib2; python_version < "3.3"',
    "docker",
    'mock; python_version < "3.3"',
    "pluggy>=0.6.0,<0.7.0",
    "pytest>=3.3.0",  # need caplog (+ warnings for tests)
    "six",
]

# Dependencies to run the tests for this Python library.
TEST_REQUIREMENTS = ["boto3", "hypothesis"]

HERE = os.path.dirname(os.path.abspath(__file__))


def setup_package():
    with io.open(
        os.path.join(HERE, "pytest_localstack", "_version.py"), "r", encoding="utf8"
    ) as f:
        about = {}
        exec(f.read(), about)

    with io.open(os.path.join(HERE, "README.rst"), "r", encoding="utf8") as f:
        readme = f.read()

    with io.open(os.path.join(HERE, "CHANGELOG.rst"), "r", encoding="utf8") as f:
        changes = f.read()

    setup(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__summary__"],
        long_description=readme + u"\n\n" + changes,
        author=about["__author__"],
        author_email=about["__author_email__"],
        license="MIT",
        url=about["__uri__"],
        packages=find_packages(where=HERE, exclude=["tests"]),
        install_requires=REQUIRES,
        tests_require=TEST_REQUIREMENTS,
        extras_require={"test": TEST_REQUIREMENTS},
        cmdclass={"test": PyTest},
        zip_safe=True,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Framework :: Pytest",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries",
            "Topic :: Software Development :: Testing",
            "Topic :: Utilities",
        ],
        entry_points={"pytest11": ["pytest-localstack = pytest_localstack"]},
    )


class PyTest(TestCommand):
    """Setup the py.test test runner."""

    def finalize_options(self):
        """Set options for the command line."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Execute the test runner command."""
        import pytest

        sys.exit(pytest.main(self.test_args))


if __name__ == "__main__":
    setup_package()
