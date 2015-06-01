from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings

import pytest
from mock import patch

from elastic_django.models import ElasticModel, ElasticModelBase
from elastic_django.exceptions import InvalidElasticsearchOperationError
from .models import Book, BookExclusion, BookSelection


@pytest.mark.django_db
class ElasticModelTestCase(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self):
        # Mock out the `index_object` method so it won't be called on saving
        # those models.
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

    def test_elastic_serializer_fields_selection(self):
        """
        Tests the ``elastic_serializer`` method when the ``ElasticModel`` is
        defined to index only a subset of its fields.
        """
        data = self.book_selection.elastic_serializer()

        self.assertDictEqual(
            data,
            {
                'title': self.book_selection.title,
                'author': self.book_selection.author,
                'pk': self.book_selection.pk
            }
        )

    def test_elastic_serializer_fields_exclusion(self):
        """
        Tests the ``elastic_serializer`` method when the ``ElasticModel`` is
        defined to exclude a subset of its fields.
        """
        data = self.book_exclusion.elastic_serializer()

        self.assertDictEqual(
            data,
            {
                'isbn': self.book_exclusion.isbn,
                'publication_year': self.book_exclusion.publication_year,
                'description': self.book_exclusion.description,
                'pk': self.book_exclusion.pk
            }
        )

    def test_elastic_serializer_all_fields(self):
        """
        Tests the ``elastic_serializer`` method when model fields are not
        defined to be indexed or excluded.
        """
        data = self.book.elastic_serializer()

        self.assertDictEqual(
            data,
            {
                'title': self.book.title,
                'author': self.book.author,
                'isbn': self.book.isbn,
                'publication_year': self.book.publication_year,
                'description': self.book.description,
                'pk': self.book.pk
            }
        )

    @patch('elastic_django.manager.ElasticManager.index_object')
    def test_auto_indexing_enabled(self, mock):
        """
        Tests that Elasticsearch indexing is triggered automatically when
        saving a new model, if selected in settings.
        """
        Book.objects.create(
            title='21st Century C', author='Ben Klemens', isbn='9781491903896',
            publication_year='2014', description='C Tips from the New School'
        )

        self.assertTrue(mock.called)

    @override_settings(ELASTICSEARCH_AUTO_INDEX=False)
    @patch('elastic_django.manager.ElasticManager.index_object')
    def test_auto_indexing_disabled(self, mock):
        """
        Tests that Elasticsearch indexing is NOT triggered when saving a new
        model, if settings are configured to avoid doing so.
        """
        Book.objects.create(
            title='21st Century C', author='Ben Klemens', isbn='9781491903896',
            publication_year='2014', description='C Tips from the New School'
        )

        self.assertFalse(mock.called)

    def test_index_delete_no_pk_error(self):
        """
        Tests error raised on trying to execute ``index_delete`` method when
        the model is not saved to the DB (doesn't have a ``pk``).
        """
        book = Book(
            title='21st Century C', author='Ben Klemens', isbn='9781491903896',
            publication_year='2014', description='C Tips from the New School'
        )

        self.assertRaisesMessage(
            InvalidElasticsearchOperationError,
            'Invalid ES backend operation: The model must be stored in DB '
            'backend prior to be deleted in Elasticsearch.',
            book.index_delete
        )

    @patch('elastic_django.manager.ElasticManager.remove_object')
    def test_auto_deleting_enabled(self, mock):
        """
        Tests that Elasticsearch deletion is triggered automatically when
        deleting a model, if selected in settings.
        """
        self.book.delete()
        self.assertTrue(mock.called)

    @override_settings(ELASTICSEARCH_AUTO_INDEX=False)
    @patch('elastic_django.manager.ElasticManager.remove_object')
    def test_auto_deleting_disabled(self, mock):
        """
        Tests that Elasticsearch deletion is NOT triggered automatically when
        deleting a model, if settings are configured to avoid doing so.
        """
        self.book.delete()
        self.assertFalse(mock.called)


class ElasticModelBaseTestCase(TestCase):
    def test_meta_index_name_string_validation(self):
        """
        Tests the validation of the extra ``Meta`` class attribute
        ``index_name``. It must be a string.
        """
        # Try to dynamically create an `ElasticModel` with a wrongly configured
        # `Meta` class. We'll repeat this in all subsequent unit tests.
        #
        # type('ElasticModel', (ElasticModel,), {
        #     'Meta': type('ElasticModelBase', (ElasticModelBase,), {
        #         '__module__': 'tests.test_models',
        #         'index_name': 432
        #     })
        # })
        self.assertRaisesMessage(
            ImproperlyConfigured,
            '`index_name` attribute must be a string.',
            type,
            'ElasticModel', (ElasticModel,), {
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'index_name': 432
                })
            }
        )

    def test_meta_elastic_fields_excludes_elastic_exclude(self):
        """
        Tests that both ``elastic_fields`` and ``elastic_exclude`` attributes
        can't live together.
        """
        self.assertRaisesMessage(
            ImproperlyConfigured,
            '`elastic_fields` and `elastic_exclude` cannot be '
            'defined together.',
            type,
            'ElasticModel', (ElasticModel,), {
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'elastic_fields': ('foo', 'bar'),
                    'elastic_exclude': ('foo', 'bar'),
                })
            }
        )

    def test_meta_elastic_fields_must_be_tuple_or_list(self):
        """
        Tests that ``elastic_fields`` attribute must be a tuple or a list.
        """
        self.assertRaisesMessage(
            ImproperlyConfigured,
            '`elastic_fields` must be a tuple or a list.',
            type,
            'ElasticModel', (ElasticModel,), {
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'elastic_fields': 'foo'
                })
            }
        )

    def test_meta_elastic_exclude_must_be_tuple_or_list(self):
        """
        Tests that ``elastic_exclude`` attribute must be a tuple or a list.
        """
        self.assertRaisesMessage(
            ImproperlyConfigured,
            '`elastic_exclude` must be a tuple or a list.',
            type,
            'ElasticModel', (ElasticModel,), {
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'elastic_exclude': 'foo'
                })
            }
        )

    def test_meta_wrong_field_name_elastic_exclude(self):
        """
        Tests that the fields specified in ``elastic_exclude`` ``Meta`` class
        attributes exists in the defined model.
        """
        self.assertRaisesMessage(
            ImproperlyConfigured,
            "The field 'foo' specified in ES Meta attributes is "
            "not defined in model 'ElasticModel'",
            type,
            'ElasticModel', (ElasticModel,), {
                '__module__': 'tests.test_models',
                'field_1': models.IntegerField(),
                'field_2': models.IntegerField(),
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'elastic_exclude': ('foo',)
                })
            }
        )

    def test_meta_wrong_field_name_elastic_fields(self):
        """
        Tests that the fields specified in ``elastic_fields`` ``Meta`` class
        attributes exists in the defined model.
        """
        self.assertRaisesMessage(
            ImproperlyConfigured,
            "The field 'foo' specified in ES Meta attributes is "
            "not defined in model 'ElasticModel'",
            type,
            'ElasticModel', (ElasticModel,), {
                '__module__': 'tests.test_models',
                'field_1': models.IntegerField(),
                'field_2': models.IntegerField(),
                'Meta': type('ElasticModelBase', (ElasticModelBase,), {
                    '__module__': 'tests.test_models',
                    'elastic_fields': ('foo',)
                })
            }
        )
