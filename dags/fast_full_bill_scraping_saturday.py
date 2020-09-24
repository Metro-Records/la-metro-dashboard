import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE, IN_SUPPORT_WINDOW
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(hours=1),
}

docker_default_args = {
    'image': 'datamade/scrapers-us-municipal',
    'volumes': [
        '{}:/app/scraper_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'))
    ],
}

docker_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'TARGET': 'bills',
    'WINDOW': 0,
    'RPM': 0,
}

with DAG(
    'fast_full_bill_scraping_saturday',
    default_args=default_args,
    schedule_interval='5 0-5 * * 6',
    description=DAG_DESCRIPTIONS['fast_full_scraping']
) as dag:

    bill_scrape = BlackboxDockerOperator(
        task_id='fast_full_bill_scrape',
        command='scraper_scripts/targeted-scrape.sh',
        environment=docker_environment,
        **docker_default_args
    )
