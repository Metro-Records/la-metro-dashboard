from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15)
}

dag = DAG(
    'sample_windowed_bill_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 5,20,35,50 * * * 0-6
)


sample_windowed_bill_scraping = BashOperator(
    task_id='windowed_bill_scraping',
    dag=dag,
    bash_command='/app/scripts/windowed-bill-scrape.sh '
)
