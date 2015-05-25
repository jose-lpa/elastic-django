import logging

try:
    # Python 3.
    from urllib.parse import urlparse
except ImportError:
    # Using Python 2.
    from urlparse import urlparse

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch.transport import Transport

class ElasticsearchClientConfigurationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        message = 'Invalid client configuration: {0}'.format(self.value)
        return repr(message)


class ElasticsearchClient(object):
    def __init__(self, hosts=None, transport_class=None, **kwargs):
        # Sanity checks.
        try:
            assert isinstance(hosts, (list, tuple))
        except AssertionError as e:
            raise ElasticsearchClientConfigurationError(e)

        auto_host = None
        if not hosts:
            auto_host = getattr(
                settings, 'ELASTICSEARCH_HOSTS', 'http://localhost:9200')

            auto_host = urlparse(auto_host)

        self.hosts = hosts or [
            {'host': auto_host.hostname, 'port': auto_host.port}]

        if not transport_class:
            self.transport = Transport

        self.connection = Elasticsearch(
            hosts=self.hosts, transport_class=self.transport, **kwargs)
