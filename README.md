# ElasticDjango

[Django](https://www.djangoproject.com/) models enhanced with [Elasticsearch](https://www.elastic.co/products/elasticsearch)
capabilities.

[![Build Status](https://travis-ci.org/jose-lpa/elastic-django.svg?branch=master)](https://travis-ci.org/jose-lpa/elastic-django)
[![Coverage Status](https://coveralls.io/repos/jose-lpa/elastic-django/badge.svg)](https://coveralls.io/r/jose-lpa/elastic-django)

### Quick start
1. Install the elastic-django package.
2. Make those models you want to be ES-enabled subclass `elastic_django.models.ElasticModel`
   instead of `django.db.models.Model`.
3. Done. A new model manager `elastic` is now available to perform ES operations.
