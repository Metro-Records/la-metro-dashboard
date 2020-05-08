import os
import sys

import django
import dj_database_url
from airflow.operators.python_operator import PythonOperator
from django.conf import settings


class DjangoOperator(PythonOperator):

    def pre_execute(self, *args, **kwargs):
        '''
        Cribbed from https://stackoverflow.com/a/50710767.
        '''
        super().pre_execute(*args, **kwargs)

        sys.path.append(os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/'))
        sys.path.append(os.getenv('SCRAPERS_DIR_PATH', '/scrapers-us-municipal/'))

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "councilmatic.settings")

        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'lametro',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'postgres',
                'PORT': 5432,
            }
        }

        settings.AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID', '')
        settings.AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY', '')

        settings.DATABASES['default'] = dj_database_url.parse(
            os.getenv(
                'LA_METRO_DATABASE_URL',
                'postgres://postgres:postgres@postgres:5432/lametro'
            ),
            conn_max_age=600
        )

        settings.HAYSTACK_CONNECTIONS['default']['URL'] = os.getenv(
            'LA_METRO_SOLR_URL',
            'http://solr:8983/solr/lametro'
        )

        django.setup()
