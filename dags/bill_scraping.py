import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator
from operators.scheduling_branch_operator import SchedulingBranchOperator


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

docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'TARGET': 'bills',
    'RPM': 60,
}

with DAG(
    'bill_scraping',
    default_args=default_args,
    schedule_interval='5,20,35,50 * * * *',
    description=DAG_DESCRIPTIONS['windowed_bill_scraping'],
) as dag:

    schedule_bill_scrape = SchedulingBranchOperator(
        task_id='schedule_bill_scrape'
    )

    regular_scrape_environment = docker_base_environment.copy()
    regular_scrape_environment['WINDOW'] = 0.05

    regular_scrape = BlackboxDockerOperator(
        task_id='regular_scrape',
        environment=regular_scrape_environment,
        **docker_default_args
    )

    broader_scrape_environment = docker_base_environment.copy()
    broader_scrape_environment['WINDOW'] = 1

    broader_scrape = BlackboxDockerOperator(
        task_id='broader_scrape',
        environment=broader_scrape_environment,
        **docker_default_args
    )

    fast_full_scrape_environment = docker_base_environment.copy()
    fast_full_scrape_environment['WINDOW'] = 0
    fast_full_scrape_environment['RPM'] = 0

    fast_full_scrape = BlackboxDockerOperator(
        task_id='fast_full_scrape',
        environment=fast_full_scrape_environment,
        **docker_default_args
    )

    no_scrape = DummyOperator(
        task_id='no_scrape'
    )

schedule_bill_scrape >> [regular_scrape, broader_scrape, fast_full_scrape, no_scrape]
