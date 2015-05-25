import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from .test_client import ElasticsearchClientTestCase
