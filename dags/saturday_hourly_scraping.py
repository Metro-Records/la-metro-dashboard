import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator

from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=1),
}

docker_default_args = {
    'image': 'datamade/scrapers-us-municipal:staging',
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

def saturday_hourly_scraping():
    if datetime.now().minute < 5:
        return 'fast_full_event_scrape'
    elif datetime.now().minute >= 5:
        return 'fast_full_bill_scrape'

with DAG(
    'saturday_hourly_scraping',
    default_args=default_args,
    schedule_interval='0,5 0-5 * * 0-6',
    description=('Run a fast full event scrape on the hour and a fast full bill scrape '
    'at 5 past the hour between midnight and 5am UTC on Saturdays (5pm to 11pm Fridays PST). '
    'Event scrape window is 0; bill scrape window is 0. '
    'Fast full scrapes scrape all bills or events quickly – that is, '
    'with requests issued as quickly as the server will respond to them. '
    'This generally takes less than 30 minutes.')
) as dag:

    branch = BranchPythonOperator(
        task_id='saturday_hourly_scraping',
        python_callable=saturday_hourly_scraping
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

    branch >> [bill_scrape, event_scrape]
