import logging

from django.conf import settings

from .client import ElasticsearchClient
from .exceptions import (
    ElasticsearchClientConfigurationError,
    ElasticsearchClientNotConnectedError)


class ElasticManager(object):
    def __init__(self):
        self._client = None
        self._connection = None

        try:
            # Attempt to connect to ES active backend(s).
            self._client = ElasticsearchClient()
            self._connection = self._client.connection
        except ElasticsearchClientConfigurationError:
            # Inform about the issue and continue, if no ES backend available.
            message = 'Elasticsearch connection unavailable.'
            logging.exception(message) if settings.DEBUG else logging.critical(
                message)

    def is_connected(self):
        """
        Checks if the manager is able to perform operations against an ES
        connected backend.
        """
        if not self._client:
            raise ElasticsearchClientNotConnectedError()

    def index_object(self, obj):
        """
        Indexes a single Django ``models.Model`` object in the ES backend.
        """
        self.is_connected()

        index_name = obj._meta.index_name or self._client.index_name

        self._connection.index(
            index=index_name,
            doc_type=obj.__class__.__name__,
            body=obj.elastic_serializer(),
            id=obj.pk
        )

        if settings.DEBUG:
            logging.debug("Indexed object '{0}' with PK '{1}' in '{2}'".format(
                obj.__class__.__name__, obj.pk, index_name))

    def remove_object(self, obj):
        """
        Removes an object from the ES backend index.
        """
        self.is_connected()

        index_name = obj._meta.index_name or self._client.index_name

        self._connection.delete(
            index=index_name,
            doc_type=obj.__class__.__name__,
            id=obj.pk
        )

        if settings.DEBUG:
            logging.debug("Deleted object '{0}' with PK '{1}' in '{2}'".format(
                obj.__class__.__name__, obj.pk, index_name))

    def get_object(self, obj):
        """
        Retrieves a specific object via its ``Model.pk`` from the ES backend.
        """
        self.is_connected()

        return self._connection.get(
            index=obj._meta.index_name or self._client.index_name,
            doc_type=obj.__class__.__name__,
            id=obj.pk
        )

    def search_match(self, index=None, **fields):
        """
        Performs a 'term' query in Elasticsearch backend for the given string.
        """
        self._connection.search(
            index=index or self._client.index_name,
            body={
                'query': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    key: fields[key]
                                }
                            } for key in fields.keys()
                        ]
                    }
                }
            }
        )

    def search_prefix(self):
        """
        Performs a 'term' query in Elasticsearch backend for the given string.
        """
        raise NotImplementedError('This search mode is not implemented.')
