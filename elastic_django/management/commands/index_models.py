from __future__ import unicode_literals

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from ...models import ElasticModel


class Command(BaseCommand):
    help = 'Triggers indexing in Elasticsearch for all models in the project' \
           ' intended to be indexed.'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label', nargs='?',
            help='App label(s) of applications to index.')

    def handle(self, *args, **options):
        app_label = options['app_label']
        if app_label:
            try:
                models = apps.get_app_config(app_label).get_models()
            except LookupError as e:
                raise CommandError(e)
        else:
            models = apps.get_models()

        checked = False
        for model in models:
            if issubclass(model, ElasticModel):
                checked = True
                items = model.objects.all()
                self.stdout.write('Indexed {0} items for model {1}.'.format(
                    len(items), model._meta.object_name))

        if not checked:
            self.stderr.write('No `ElasticModel` models found to be indexed.')
