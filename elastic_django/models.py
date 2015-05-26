from django.conf import settings
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import six
from django.utils.encoding import force_str

from .manager import ElasticManager


class ElasticModelBase(models.base.ModelBase):
    """
    Custom implementation of ``ModelBase`` which adds some new ``Meta`` options
    to the ``Model`` class.
    """
    def __new__(mcs, name, bases, attrs):
        """
        Overrides base ``__new__`` method to retrieve and clean the custom
        Elasticsearch ``Meta`` attributes, if any.
        """
        elastic_meta = {}
        if 'Meta' in attrs:
            # TODO: Clean this properly:
            # 1) Check consistency of objects - the `index_name` must be a string, the `elastic_*` must be tuples of strings...
            # 2) Raise `ImproperlyConfigured` errors when needed.
            if hasattr(attrs['Meta'], 'index_name'):
                elastic_meta['index_name'] = attrs['Meta'].index_name
                delattr(attrs['Meta'], 'index_name')
            if hasattr(attrs['Meta'], 'elastic_fields'):
                # Sanity check.
                if hasattr(attrs['Meta'], 'elastic_exclude'):
                    raise ImproperlyConfigured(
                        '`elastic_fields` and `elastic_exclude` cannot be '
                        'defined together.')

                elastic_meta['elastic_fields'] = attrs['Meta'].elastic_fields
                delattr(attrs['Meta'], 'elastic_fields')
            if hasattr(attrs['Meta'], 'elastic_exclude'):
                elastic_meta['elastic_exclude'] = attrs['Meta'].elastic_exclude
                delattr(attrs['Meta'], 'elastic_exclude')

        new_class = super(ElasticModelBase, mcs).__new__(
            mcs, name, bases, attrs)

        if hasattr(new_class, '_meta'):
            # Append the custom attributes to the Django `Model.Meta` class.
            new_class._meta.index_name = elastic_meta.get('index_name', None)
            new_class._meta.elastic_fields = elastic_meta.get(
                'elastic_fields', None)
            new_class._meta.elastic_exclude = elastic_meta.get(
                'elastic_exclude', None)

        return new_class


class ElasticModel(models.Model):
    """
    Subclass of Django ``models.Model`` extended with Elasticsearch
    capabilities.
    """
    # Engage `ElasticModelBase` to extend the base Django `Model.Meta` class.
    __metaclass__ = ElasticModelBase

    # Custom ES model manager.
    elastic = ElasticManager()

    class Meta:
        abstract = True

    def __repr__(self):
        try:
            u = six.text_type(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return force_str('<{0}: {1} w/ES>'.format(self.__class__.__name__, u))

    def save(self, *args, **kwargs):
        """
        Overrides base Django ``models.Model.save`` method to implement
        automatic Elasticsearch indexing.

        By default, this implementation will automatically index/update the
        current model instance in any ``save`` call. This behaviour can be
        changed by setting ``ELASTICSEARCH_AUTO_INDEX`` to ``False``.
        """
        super(ElasticModel, self).save(*args, **kwargs)

        # self.elastic.client.connection.index()

    def elastic_serializer(self):
        """
        ``Model`` serialization to be used for creating JSON data to be sent to
        Elasticsearch backend.

        Takes a look over the custom ``Meta`` attributes, to check if there are
        any definitions that may affect the number of fields to be serialized.
        If there are no restrictions, it will serialize all fields.

        :return: A JSON dataset representing this model instance serialized.
        """
        pass
        # if hasattr(self._meta, 'elastic_fields'):

