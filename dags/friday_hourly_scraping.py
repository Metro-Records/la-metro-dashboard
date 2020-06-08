from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator

from base import SCRAPERS_DIR_PATH

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=3)
}

dag = DAG(
    'friday_hourly_scraping',
    default_args=default_args,
    schedule_interval='0,5 21-23 * * 5',
    description=('Run a fast full event scrape on the hour and a fast full bill scrape '
    'at 5 past the hour between 9pm and midnight UTC on Fridays (2pm to 5pm Fridays PST). '
    'Event scrape window is 0; bill scrape window is 0. '
    'Fast full scrapes scrape all bills or events quickly – that is, '
    'with requests issued as quickly as the server will respond to them. '
    'This generally takes less than 30 minutes.')
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
    params={'window': 0, 'target': 'bills', 'rpm': 0, 'scrapers_dir_path': SCRAPERS_DIR_PATH},
    bash_command='scripts/targeted-scrape.sh'
)

event_scrape = BashOperator(
    task_id='fast_full_event_scrape',
    dag=dag,
    params={'window': 0, 'target': 'events', 'rpm': 0, 'scrapers_dir_path': SCRAPERS_DIR_PATH},
    bash_command='scripts/targeted-scrape.sh'
)

branch >> [bill_scrape, event_scrape]
