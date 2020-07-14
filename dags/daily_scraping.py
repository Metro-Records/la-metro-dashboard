import os
from datetime import datetime, timedelta

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=12),
    'image': 'datamade/scrapers-us-municipal:staging',
    'environment': {
        'DECRYPTED_SETTINGS': 'pupa_settings.py',
        'DESTINATION_SETTINGS': 'pupa_settings.py',
        'DATABASE_URL': LA_METRO_DATABASE_URL,
    },
    'volumes': [
        '{}:/app/scraper_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'))
    ],
}

with DAG(
    'daily_scraping',
    default_args=default_args,
    schedule_interval='5 0 * * 0-5',
    description=('Scrape all people and committees, bills, and events “politely” '
    '– that is, with requests throttled to 60 per minute, or 1 per second. '
    'This generally takes 6-7 hours.')
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='daily_scraping',
        command='scraper_scripts/full-scrape.sh'
    )
