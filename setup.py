#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='elastic-django',
    version='0.1',
    description='Elasticsearch enhancements for Django models.',
    author='Jose L. Patino Andres',
    author_email='jose.lpa@gmail.com',
    url='http://patino.me',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'elasticsearch',
        'elasticsearch-dsl',
        'Django>=1.8'
    ],
    test_suite='tests',
    tests_require=[
        'mock',
        'pytest-django',
        'pytest-cov',
        'pytest-pep8',
    ],
    cmdclass={'test': PyTest},
)
