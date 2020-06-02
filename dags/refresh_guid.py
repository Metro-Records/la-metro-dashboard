from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator
from django.core.management import call_command

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'guid_log',
    default_args=default_args,
    schedule_interval='0 1 * * *',
    description="Refresh GUID log."
)

def refresh_guid():
    call_command('refresh_guid')


t1 = DjangoOperator(
    task_id='refresh_guid',
    dag=dag,
    python_callable=refresh_guid
)
