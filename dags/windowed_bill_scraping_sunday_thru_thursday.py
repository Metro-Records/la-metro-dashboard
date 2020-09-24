import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE, IN_SUPPORT_WINDOW
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(hours=3)
}

docker_default_args = {
    'image': 'datamade/scrapers-us-municipal',
    'volumes': [
        '{}:/app/scraper_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'))
    ],
    'command': 'scraper_scripts/targeted-scrape.sh',
}

docker_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'TARGET': 'bills',
    'WINDOW': 0.05,
    'RPM': 60,
}

with DAG(
    'windowed_bill_scraping_sunday_thru_thursday',
    default_args=default_args,
    schedule_interval='5,20,35,50 0-20 * * 5',
    description=DAG_DESCRIPTIONS['windowed_bill_scraping']
) as dag:

    windowed_bill_scrape = BlackboxDockerOperator(
        task_id='windowed_bill_scrape',
        environment=docker_environment,
        **docker_default_args
    )
