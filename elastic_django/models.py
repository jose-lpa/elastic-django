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
            if hasattr(attrs['Meta'], 'index_name'):
                elastic_meta['index_name'] = attrs['Meta'].index_name
                delattr(attrs['Meta'], 'index_name')
            if hasattr(attrs['Meta'], 'elastic_fields'):
                elastic_meta['index_name'] = attrs['Meta'].elastic_fields
                delattr(attrs['Meta'], 'elastic_fields')

        new_class = super(ElasticModelBase, mcs).__new__(
            mcs, name, bases, attrs)

        if hasattr(new_class, '_meta'):
            new_class._meta.index_name = elastic_meta.get('index_name', None)
            new_class._meta.elastic_fields = elastic_meta.get(
                'elastic_fields', None)

        return new_class


class ElasticModel(models.Model):
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Overrides base Django ``models.Model.save`` method to implement
        automatic Elasticsearch, if defined in settings.
        """
        super(ElasticModel, self).save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields)

        # self.elastic.client.connection.index()
