import logging

from django.conf import settings

from elasticsearch.transport import Transport
from elasticsearch_dsl import connections

from .exceptions import ElasticsearchClientConfigurationError


class ElasticsearchClient(object):
    def __init__(self, hosts=None, transport_class=None, **kwargs):
        """
        Initialization of the Elasticsearch client.

        :param hosts: List of dictionaries specifying the parameters of node(s)
        to be connected to. Examples (from ``elasticsearch-py`` package):
            - ``['localhost:9200']``
            - ``['localhost:443', 'another_node:443']``
            - ``['http://user:secret@localhost:9200/']``
            - ``[
                    {'host': 'localhost'},
                    {
                        'host': 'node-2', 'port': 443, 'url_prefix': 'es',
                        'use_ssl': True
                    },
                ]``
        :param transport_class: The ``elasticsearch.transport.Transport``
        subclass to be used, if any.
        :param kwargs: Additional parameters to be passed to ``Transport``
        class instance.
        """
        # Sanity checks.
        if hosts:
            try:
                assert isinstance(hosts, (list, tuple))
                self.hosts = hosts
            except AssertionError as e:
                raise ElasticsearchClientConfigurationError(e)
        else:
            # No hosts given in client construct. Fallback to specified Django
            # settings. Otherwise, automatic configuration to default ES node.
            settings_hosts = getattr(
                settings, 'ELASTICSEARCH_HOSTS', None)
            if settings_hosts:
                self.hosts = settings_hosts
            else:
                self.hosts = [{'host': 'localhost', 'port': '9200'}]

        if not transport_class:
            self.transport = Transport

        self.connection = connections.connections.create_connection(
            hosts=self.hosts, transport_class=self.transport, **kwargs)

        # Define the ES index name to be used everywhere.
        self.index_name = getattr(
            settings, 'ELASTICSEARCH_INDEX_NAME', 'elastic-django')

        self.connection.indices.create(index=self.index_name, ignore=400)

        # Check connection before continuing.
        if not self.connection.ping():
            raise ElasticsearchClientConfigurationError(
                'Elasticsearch backend unreachable. Check host configuration.')
        else:
            logging.debug(
                "Connection established with Elasticsearch backend(s) in "
                "'{0}'".format(self.connection.transport.hosts))
