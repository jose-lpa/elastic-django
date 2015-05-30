from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase

import pytest

from elastic_django.models import ElasticModel, ElasticModelBase
from .models import Book


@pytest.mark.django_db
class ElasticModelTestCase(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self):
        self.book = Book.objects.create(
            title='Effective Python', author='Brett Slatkin',
            isbn='9780134034287', publication_year=2015,
            description='59 Specific Ways to Write Better Python.')

    def test_meta_index_name_must_string(self):
        """
        Test this thingy to check that Django database is enabled.
        """
        self.assertEqual(self.book.title, 'Effective Python')


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
