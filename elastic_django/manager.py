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
        return self._client is not None

    def index_object(self, obj):
        """
        Indexes a single Django ``models.Model`` object in the ES backend.
        """
        import pdb
        pdb.set_trace()
        if not self.is_connected():
            raise ElasticsearchClientNotConnectedError()

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
        if not self.is_connected():
            raise ElasticsearchClientNotConnectedError()

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
        if not self.is_connected():
            raise ElasticsearchClientNotConnectedError()

        index_name = obj._meta.index_name or self._client.index_name

        return self._connection.get(
            index=index_name,
            doc_type=obj.__class__.__name__,
            id=obj.pk
        )
