from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=3)
}

dag = DAG(
    'friday_hourly_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,5 21-23 * * 5
)

def friday_hourly_scraping():
    if datetime.now().minute < 5:
        return 'fast_full_event_scrape'
    elif datetime.now().minute >= 5:
        return 'fast_full_bill_scrape'


branch = BranchPythonOperator(
    task_id='friday_hourly_scraping',
    dag=dag,
    python_callable=friday_hourly_scraping
)

bill_scrape = BashOperator(
    task_id='fast_full_bill_scrape',
    dag=dag,
    bash_command='/app/scripts/fast-full-bill-scrape.sh '
)

event_scrape = BashOperator(
    task_id='fast_full_event_scrape',
    dag=dag,
    bash_command='/app/scripts/fast-full-event-scrape.sh '
)

branch >> [bill_scrape, event_scrape]
