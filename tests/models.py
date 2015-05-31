from django.db import models

from elastic_django.models import ElasticModel


class Book(ElasticModel):
    """
    Main 'Book' model.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    publication_year = models.SmallIntegerField()
    description = models.TextField(blank=True)


class BookSelection(ElasticModel):
    """
    'Book' model with a selection of fields to be indexed.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    publication_year = models.SmallIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        elastic_fields = ('title', 'author')


class BookExclusion(ElasticModel):
    """
    'Book' model with a selection of fields to be excluded from index.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, null=True, blank=True)
    publication_year = models.SmallIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        elastic_exclude = ('title', 'author')
