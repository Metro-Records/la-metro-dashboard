import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE
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

docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'WINDOW': 0,
    'RPM': 0,
}

def fast_full_scraping():
    now = datetime.now()

    friday_night = now.weekday == 5 and now.hour >= 21
    saturday_morning = now.weekday == 6 and now.hour <= 5

    if friday_night or saturday_morning:
        if datetime.now().minute < 5:
            return 'fast_full_event_scrape'
        elif datetime.now().minute >= 5:
            return 'fast_full_bill_scrape'

    else:
        return 'no_scrape'

with DAG(
    'fast_full_scraping',
    default_args=default_args,
    schedule_interval='0,5 * * * 5,6',
    description=DAG_DESCRIPTIONS['fast_full_scraping']
) as dag:

    branch = BranchPythonOperator(
        task_id='fast_full_scraping',
        python_callable=fast_full_scraping
    )

    bill_environment = docker_base_environment.copy()
    bill_environment['TARGET'] = 'bills'

    bill_scrape = BlackboxDockerOperator(
        task_id='fast_full_bill_scrape',
        command='scraper_scripts/targeted-scrape.sh',
        environment=bill_environment,
        **docker_default_args
    )

    event_environment = docker_base_environment.copy()
    event_environment['TARGET'] = 'events'

    event_scrape = BlackboxDockerOperator(
        task_id='fast_full_event_scrape',
        command='scraper_scripts/targeted-scrape.sh',
        environment=event_environment,
        **docker_default_args
    )

    no_scrape = DummyOperator(
        task_id='no_scrape'
    )

branch >> [bill_scrape, event_scrape, no_scrape]
