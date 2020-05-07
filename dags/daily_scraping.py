import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators import BashOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'daily_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 5 0 * * 0-6
)


t1 = BashOperator(
    task_id='daily_scraping',
    dag=dag,
    bash_command='/app/scripts/full-scrape.sh '
)
