import sys

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator
from django.core.management import call_command

one_am_today = datetime.now().replace(hour=1)

default_args = {
    'start_date': one_am_today,
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'guid_log',
    default_args=default_args,
    schedule_interval=None # eventually '0 1 * * *'
)

APPDIR = '/home/datamade/lametro'
PYTHONDIR = '/home/datamade/.virtualenvs/lametro/bin/python'

def refresh_guid():
    call_command('refresh_guid')


t1 = DjangoOperator(
    task_id='refresh_guid',
    dag=dag,
    python_callable=refresh_guid
)
