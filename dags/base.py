import os
import sys

import django
import dj_database_url
from airflow.operators.python_operator import PythonOperator
from django.conf import settings

SCRAPERS_DIR_PATH = os.getenv('SCRAPERS_DIR_PATH', '/scrapers-us-municipal/')
LA_METRO_DIR_PATH = os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/')
LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')


class DjangoOperator(PythonOperator):

    def pre_execute(self, *args, **kwargs):
        '''
        Cribbed from https://stackoverflow.com/a/50710767.
        '''
        super().pre_execute(*args, **kwargs)

        self.setup_django()

    @classmethod
    def setup_django(cls):
        """
        Run django.setup() with appropriate values for running commands against
        la-metro-councilmatic and scrapers-us-municipal.
        """
        sys.path.append(LA_METRO_DIR_PATH)
        sys.path.append(SCRAPERS_DIR_PATH)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "councilmatic.settings")

        settings.AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID', '')
        settings.AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY', '')

        settings.DATABASES = {}
        settings.DATABASES['default'] = dj_database_url.parse(
            LA_METRO_DATABASE_URL,
            conn_max_age=600
        )

        settings.HAYSTACK_CONNECTIONS['default']['URL'] = os.getenv(
            'LA_METRO_SOLR_URL',
            'http://solr:8983/solr/lametro'
        )

        django.setup()
