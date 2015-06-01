import json

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import six
from django.utils.encoding import force_str

from .exceptions import InvalidElasticsearchOperationError
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
            if hasattr(attrs['Meta'], 'index_name'):
                index_name = attrs['Meta'].index_name
                if not isinstance(index_name, six.string_types):
                    raise ImproperlyConfigured(
                        '`index_name` attribute must be a string.')

                elastic_meta['index_name'] = index_name
                delattr(attrs['Meta'], 'index_name')

            if hasattr(attrs['Meta'], 'elastic_fields'):
                if hasattr(attrs['Meta'], 'elastic_exclude'):
                    # `elastic_fields` and `elastic_exclude` are exclusive.
                    raise ImproperlyConfigured(
                        '`elastic_fields` and `elastic_exclude` cannot be '
                        'defined together.')

                elastic_fields = attrs['Meta'].elastic_fields
                if not isinstance(elastic_fields, (tuple, list)):
                    raise ImproperlyConfigured(
                        '`elastic_fields` must be a tuple or a list.')

                elastic_meta['elastic_fields'] = elastic_fields
                delattr(attrs['Meta'], 'elastic_fields')
            elif hasattr(attrs['Meta'], 'elastic_exclude'):
                elastic_exclude = attrs['Meta'].elastic_exclude
                if not isinstance(elastic_exclude, (tuple, list)):
                    raise ImproperlyConfigured(
                        '`elastic_exclude` must be a tuple or a list.')

                elastic_meta['elastic_exclude'] = elastic_exclude
                delattr(attrs['Meta'], 'elastic_exclude')

            fields = elastic_meta.get('elastic_fields') or elastic_meta.get(
                'elastic_exclude') or []
            for field in fields:
                if field not in attrs or not isinstance(
                        attrs[field], models.fields.Field):
                    raise ImproperlyConfigured(
                        "The field '{0}' specified in ES Meta attributes is "
                        "not defined in model '{1}'".format(field, name))

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


class ElasticModel(six.with_metaclass(ElasticModelBase, models.Model)):
    """
    Subclass of Django ``models.Model`` extended with Elasticsearch
    capabilities.
    """
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

        if getattr(settings, 'ELASTICSEARCH_AUTO_INDEX', True):
            self.index()

    def delete(self, using=None):
        """
        Overrides base Django ``models.Model.delete`` method to implemente
        automatic Elasticsearch deletion.
        """
        if getattr(settings, 'ELASTICSEARCH_AUTO_INDEX', True):
            self.index_delete()

        super(ElasticModel, self).delete(using)

    def index(self):
        """
        Index the object in Elasticsearch backend.
        """
        self.elastic.index_object(self)

    def index_delete(self):
        """
        Remove the object from the Elasticsearch index. Note that this won't
        affect the Django DB backend object at all.
        """
        if not self.pk:
            raise InvalidElasticsearchOperationError(
                'The model must be stored in DB backend prior to be deleted in'
                ' Elasticsearch.')

        self.elastic.remove_object(self.pk)

    def elastic_serializer(self):
        """
        ``Model`` serialization to be used for creating JSON data to be sent to
        Elasticsearch backend.

        Takes a look over the custom ``Meta`` attributes, to check if there are
        any definitions that may affect the number of fields to be serialized.
        If there are no restrictions, it will serialize all fields.

        :return: A JSON-serializable data set representing this model instance
        serialized.
        """
        if self._meta.elastic_fields:
            # Serialize only custom fields here (plus the mandatory object PK).
            data = serializers.serialize(
                'json', [self], fields=self._meta.elastic_fields)
        elif self._meta.elastic_exclude:
            # Serialize all the fields of the model here, except those marked
            # as to be excluded.
            fields = []
            for field in self._meta.fields:
                if field.name not in self._meta.elastic_exclude:
                    fields.append(field.name)
            data = serializers.serialize('json', [self], fields=fields)
        else:
            # Serialize all fields.
            data = serializers.serialize('json', [self])

        data = json.loads(data)
        doc = data[0]['fields']
        doc.update({'pk': data[0]['pk']})

        return doc
