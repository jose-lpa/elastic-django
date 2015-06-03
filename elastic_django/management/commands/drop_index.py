from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from elasticsearch.exceptions import NotFoundError

from ...client import ElasticsearchClient
from ...exceptions import ElasticsearchClientConfigurationError

class Command(BaseCommand):
    help = 'Entirely removes a search index from Elasticsearch backend. USE ' \
           'IT WITH CAUTION.'

    def add_arguments(self, parser):
        parser.add_argument(
            'index_name', nargs=1,
            help='Name of the Elasticsearch index to be removed.')

    def handle(self, *args, **options):
        try:
            client = ElasticsearchClient()
        except ElasticsearchClientConfigurationError as e:
            raise CommandError(e)

        index_name = options['index_name']
        if not index_name:
            index_name = getattr(
                settings, 'ELASTICSEARCH_INDEX_NAME', 'elastic-django')
            if not client.connection.indices.exists(index_name):
                raise CommandError(
                    'No Elasticsearch index name defined and no autoconfigured'
                    ' indices found to remove. Please specify an index name.')

        try:
            response = client.connection.indices.delete(index_name)
            if response.get('acknowledged', False):
                self.stdout.write("Dropped Elasticsearch index '{0}'".format(
                    index_name))
            else:
                self.stdout.write("Something occurred. Elasticsearch index "
                                  "'{0}' was not dropped.".format(index_name))
        except NotFoundError:
            raise CommandError("No index called '{0}' found in Elasticsearch "
                               "backend.".format(index_name))
