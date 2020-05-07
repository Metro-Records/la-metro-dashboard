import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators import BashOperator, BranchPythonOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=1)
}

dag = DAG(
    'friday_hourly_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,5 21-23 * * 5
)

def friday_hourly_scraping():
    if datetime.now().minute < 5:
        return 'fast-full-event-scrape'
    elif datetime.now().minute >= 5:
        return 'fast-full-bill-scrape'


branch = BranchPythonOperator(
    task_id='friday_hourly_scraping',
    dag=dag,
    python_callable=friday_hourly_scraping
)

bill_scrape = BashOperator(
    task_id='fast-full-bill-scrape',
    dag=dag,
    bash_command='/app/scripts/fast-full-bill-scrape'
)

event_scrape = BashOperator(
    task_id='fast-full-event-scrape',
    dag=dag,
    bash_command='/app/scripts/fast-full-event-scrape'
)

branch >> [bill_scrape, event_scrape]
