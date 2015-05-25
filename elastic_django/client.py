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

from .exceptions import ElasticsearchClientConfigurationError


class ElasticsearchClient(object):
    def __init__(self, hosts=None, transport_class=None, **kwargs):
        # Sanity checks.
        if hosts:
            try:
                assert isinstance(hosts, (list, tuple))
                self.hosts = hosts
            except AssertionError as e:
                raise ElasticsearchClientConfigurationError(e)
        else:
            # No hosts given. Automatic configuration to default ES node.
            auto_host = getattr(
                settings, 'ELASTICSEARCH_HOSTS', 'http://localhost:9200')
            auto_host = urlparse(auto_host)
            self.hosts = [{'host': auto_host.hostname, 'port': auto_host.port}]

        if not transport_class:
            self.transport = Transport

        self.connection = Elasticsearch(
            hosts=self.hosts, transport_class=self.transport, **kwargs)

        # Check connection before continuing.
        if not self.connection.ping():
            raise ElasticsearchClientConfigurationError(
                'Elasticsearch backend unreachable. Check host configuration.')
        else:
            logging.debug(
                "Connection established with Elasticsearch backend(s) in "
                "'{0}'".format(self.connection.transport.hosts))
