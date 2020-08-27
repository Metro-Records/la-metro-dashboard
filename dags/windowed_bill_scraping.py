import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE
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

docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'TARGET': 'bills',
    'RPM': 60,
}

def handle_scheduling():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 35,50 minutes
    now = datetime.now()

    if now.weekday == 5 and now.hour >= 9:
        if now.minute < 35:
            return 'no_scrape'
        return 'larger_windowed_bill_scrape'

    elif now.weekday == 6 and now.hour <= 5:
        if now.minute < 35:
            return 'no_scrape'
        return 'larger_windowed_bill_scrape'

    return 'windowed_bill_scrape'

with DAG(
    'windowed_bill_scraping',
    default_args=default_args,
    schedule_interval='5,20,35,50 * * * 0-6',
    description=DAG_DESCRIPTIONS['windowed_bill_scraping']
) as dag:

    branch = BranchPythonOperator(
        task_id='handle_scheduling',
        python_callable=handle_scheduling
    )

    windowed_bill_scrape_environment = docker_base_environment.copy()
    windowed_bill_scrape_environment['WINDOW'] = 0.05

    windowed_bill_scrape = BlackboxDockerOperator(
        task_id='windowed_bill_scrape',
        environment=windowed_bill_scrape_environment,
        **docker_default_args
    )

    larger_windowed_bill_scrape_environment = docker_base_environment.copy()
    larger_windowed_bill_scrape_environment['WINDOW'] = 1

    larger_windowed_bill_scrape = BlackboxDockerOperator(
        task_id='larger_windowed_bill_scrape',
        environment=larger_windowed_bill_scrape_environment,
        **docker_default_args
    )

    no_scrape = DummyOperator(
        task_id='no_scrape'
    )

branch >> [windowed_bill_scrape, larger_windowed_bill_scrape, no_scrape]
