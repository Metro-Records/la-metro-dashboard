from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=12)
}

dag = DAG(
    'daily_scraping',
    default_args=default_args,
    schedule_interval='5 0 * * 0-5',
    description=('Scrape all people and committees, bills, and events “politely” '
    '– that is, with requests throttled to 60 per minute, or 1 per second. '
    'This generally takes 6-7 hours.')
)


t1 = BashOperator(
    task_id='daily_scraping',
    dag=dag,
    bash_command='scripts/full-scrape.sh'
)
