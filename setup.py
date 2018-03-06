#!/usr/bin/env python
import contextlib
import io
import os
import sys

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command.test import test as TestCommand

# Dependencies for this Python library.
REQUIRES = [
    'botocore>=1.4.31,!=1.4.45',
    'contextlib2; python_version < "3.3"',
    'docker',
    'pluggy>=0.6.0,<0.7.0',
    'pytest>=3.0.0',
    'six',
]

# Dependencies to run the tests for this Python library.
TEST_REQUIREMENTS = [
    'boto3',
    'hypothesis[faker]',
    'pytest-cov',
]

HERE = os.path.dirname(os.path.abspath(__file__))


def setup_package():
    with chdir(HERE):
        packages = find_packages(exclude=['docs', 'tests'])

        with io.open(os.path.join('pytest_localstack', '_version.py'), 'r', encoding='utf8') as f:
            about = {}
            exec(f.read(), about)

        with io.open('README.rst', 'r', encoding='utf8') as f:
            readme = f.read()

    setup(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__summary__'],
        long_description=readme,
        author=about['__author__'],
        author_email=about['__author_email__'],
        license='MIT',
        url=about['__uri__'],
        packages=packages,
        install_requires=REQUIRES,
        tests_require=TEST_REQUIREMENTS,
        extras_require={'test': TEST_REQUIREMENTS},
        cmdclass={'test': PyTest},
        zip_safe=True,
        classifiers=(
            'Development Status :: 2 - Pre-Alpha',
            'License :: OSI Approved :: MIT License',
            'Framework :: Pytest',
            'Intended Audience :: Developers',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Utilities',
        ),
        entry_points={
            'pytest11': [
                'pytest-localstack = pytest_localstack',
            ]
        },
    )


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


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
