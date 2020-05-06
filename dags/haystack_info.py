from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator
from django.core.management import call_command


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'haystack_info',
    default_args=default_args,
    schedule_interval=None
)


def haystack_info():
    call_command('haystack_info')


t1 = DjangoOperator(
    task_id='haystack_info',
    dag=dag,
    python_callable=haystack_info
)
