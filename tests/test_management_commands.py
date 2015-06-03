from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

import pytest
from mock import patch

from .models import Book, BookExclusion, BookSelection


@pytest.mark.django_db
class IndexModelsTestCase(TestCase):
    """
    Tests for ``index_models`` custom management command.
    """
    pytestmark = pytest.mark.django_db

    def setUp(self):
        with patch('elastic_django.manager.ElasticManager.index_object'):
            self.book = Book.objects.create(
                title='Effective Python', author='Brett Slatkin',
                isbn='9780134034287', publication_year=2015,
                description='59 Specific Ways to Write Better Python.')

            # `Book` model with only `title` and `author` fields selected to
            # index.
            self.book_selection = BookSelection.objects.create(
                title='Effective Java', author='Joshua Bloch',
                isbn='9780321356680', publication_year=2009,
                description='The best Java book yet written.... Really great; '
                            'very readable and eminently useful.')

            # `Book` model with `title` and `author` fields selected to be
            # excluded from index.
            self.book_exclusion = BookExclusion.objects.create(
                title='Effective C++', author='Scott Meyers',
                isbn='9780321334879', publication_year=2008,
                description='55 Specific Ways to Improve Your Programs.')

    def test_bad_app_label_provided(self):
        """
        Tests the command behaviour when user provides a non existent app label
        in the CLI.
        """
        self.assertRaises(
            CommandError, call_command, 'index_models', 'non-existent-app')
