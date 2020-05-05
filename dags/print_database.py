from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'councilmatic_showmigrations',
    default_args=default_args,
    schedule_interval=None
)


def print_database():
    from django.conf import settings
    print(settings.DATABASES['default']['host'])


t1 = DjangoOperator(
    task_id='print_database',
    dag=dag,
    python_callable=print_database
)
