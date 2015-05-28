SECRET_KEY = 'Elasticsearch meets Django'

DATABASES = {
    'default': {
        # Memory resident database, for easy testing.
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = ['tests']

# Elastic-Django custom settings.
ELASTICSEARCH_HOSTS = [{'host': 'localhost', 'port': '9200'}]
ELASTICSEARCH_TRANSPORT_CLASS = None
ELASTICSEARCH_INDEX_NAME = 'testing-elasticdjango'
ELASTICSEARCH_AUTO_INDEX = True
