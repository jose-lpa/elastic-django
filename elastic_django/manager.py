import logging

from django.conf import settings

from .client import ElasticsearchClient
from .exceptions import ElasticsearchClientConfigurationError


# logger = getLogger('elastic_django')


class ElasticManager(object):
    def __init__(self):
        try:
            self.client = ElasticsearchClient()
        except ElasticsearchClientConfigurationError:
            message = 'Elasticsearch connection unavailable.'
            logging.exception(message) if settings.DEBUG else logging.critical(
                message)
