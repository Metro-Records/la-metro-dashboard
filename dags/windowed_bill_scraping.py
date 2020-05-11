from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=3)
}

dag = DAG(
    'windowed_bill_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 5,20,35,50 * * * 0-6
)

def handle_scheduling():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 35,50 minutes
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9 and now.minute < 35:
        return 'no_scrape'
    elif now.weekday == 6 and now.hour <= 5 and now.minute < 35:
        return 'no_scrape'
    else:
        return 'windowed_bill_scraping'


branch = BranchPythonOperator(
    task_id='handle_scheduling',
    dag=dag,
    python_callable=handle_scheduling
)

windowed_bill_scraping = BashOperator(
    task_id='windowed_bill_scraping',
    dag=dag,
    bash_command='/app/scripts/windowed-bill-scrape.sh '
)

no_scrape = DummyOperator(
    task_id='no_scrape',
    dag=dag
)

branch >> [windowed_bill_scraping, no_scrape]
