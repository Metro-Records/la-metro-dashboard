from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from base import SCRAPERS_DIR_PATH, LA_METRO_DATABASE_URL

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
    params={
        'scrapers_dir_path': SCRAPERS_DIR_PATH,
        'la_metro_database_url': LA_METRO_DATABASE_URL
    },
    bash_command='scripts/full-scrape.sh'
)
