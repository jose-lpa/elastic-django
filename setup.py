#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='elastic-django',
    version='0.1',
    description='Elasticsearch enhancements for Django models.',
    author='Jose L. Patino Andres',
    author_email='jose.lpa@gmail.com',
    url='http://patino.me',
    packages=find_packages(),
    install_requires=['elasticsearch', 'Django>=1.8'],
    test_suite='tests'
)
