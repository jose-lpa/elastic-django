from .client import ElasticsearchClient


class ElasticManager(object):
    def __init__(self):
        self.client = ElasticsearchClient()
