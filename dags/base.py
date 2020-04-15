import os
import sys

from airflow.models import BaseOperator
from airflow.operators.python_operator import PythonOperator
import django
from django.conf import settings


class DjangoOperator(PythonOperator):

    def pre_execute(self, *args, **kwargs):
        '''
        Cribbed from https://stackoverflow.com/a/50710767.
        '''
        super().pre_execute(*args, **kwargs)

        sys.path.append("/la-metro-councilmatic/")

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

        django.setup()