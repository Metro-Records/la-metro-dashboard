from datetime import timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(hours=12),
    'image': 'datamade/scrapers-us-municipal',
    'environment': {
        'DECRYPTED_SETTINGS': 'pupa_settings.py',
        'DESTINATION_SETTINGS': 'pupa_settings.py',
        'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    },
    'volumes': [
        '{}:/app/scraper_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'))
    ],
}

with DAG(
    'daily_scraping',
    default_args=default_args,
    schedule_interval='5 0 * * 0-5',
    description=DAG_DESCRIPTIONS['daily_scraping']
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='daily_scraping',
        command='scraper_scripts/full-scrape.sh'
    )
