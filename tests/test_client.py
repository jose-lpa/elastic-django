from unittest import TestCase

from django.conf import settings
from django.test.utils import override_settings

from mock import patch

from elastic_django.client import ElasticsearchClient
from elastic_django.exceptions import ElasticsearchClientConfigurationError


class ElasticsearchClientTestCase(TestCase):
    def test_client_constructor_sanity_check(self):
        """
        Tests sanity checks in ``ElasticsearchClient.__init__``.
        """
        self.assertRaises(
            ElasticsearchClientConfigurationError,
            ElasticsearchClient,
            hosts='not a list or tuple'
        )

    @override_settings(ELASTICSEARCH_HOSTS=None)
    @patch('elasticsearch.Elasticsearch.ping')
    def test_no_hosts_given_nor_configured(self, mock):
        """
        Tests client behaviour when being called with no hosts specified and no
        hosts defined in Django settings. It should fallback to the ES default
        expected configuration (localhost, port 9200).
        """
        # Delete setting.
        del settings.ELASTICSEARCH_HOSTS

        # Mock ES backend ping response to pass test.
        mock.return_value = True

        client = ElasticsearchClient()
        self.assertEqual(client.hosts, [{'host': 'localhost', 'port': '9200'}])

    @override_settings(
        ELASTICSEARCH_HOSTS=[{'host': '127.0.0.1', 'port': '443'}])
    @patch('elasticsearch.Elasticsearch.ping')
    def test_no_hosts_given_and_configured(self, mock):
        """
        Tests client behaviour when being called with no hosts specified and
        hosts already defined in Django settings.
        """
        # Mock ES backend ping response to pass test.
        mock.return_value = True

        client = ElasticsearchClient()

        self.assertEqual(client.hosts, [{'host': '127.0.0.1', 'port': '443'}])

    @override_settings(
        ELASTICSEARCH_HOSTS=[{'host': '127.0.0.1', 'port': '9999'}])
    def test_no_ping_response(self):
        """
        Tests exception raised when backend doesn't respond to ping - specified
        backend is unavailable.
        """
        self.assertRaises(
            ElasticsearchClientConfigurationError, ElasticsearchClient)
