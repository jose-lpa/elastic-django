
class ElasticsearchClientConfigurationError(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr('Invalid client configuration: {0}'.format(self.value))
        return 'Invalid client configuration'
