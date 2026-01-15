import os
from datetime import timedelta

from airflow import DAG
from docker.types import Mount

from constants import (
    LA_METRO_DATABASE_URL,
    LA_METRO_STAGING_DATABASE_URL,
    AIRFLOW_DIR_PATH,
    START_DATE,
    ENVIRONMENT,
    LA_SCRAPERS_IMAGE_URL,
)
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(hours=18),
}

default_docker_args = {
    "image": LA_SCRAPERS_IMAGE_URL,
    "mounts": [
        Mount(
            source=os.path.join(AIRFLOW_DIR_PATH, "dags", "scripts"),
            target="/app/scraper_scripts",
            type="bind",
        ),
    ],
    "command": "scraper_scripts/targeted-scrape.sh",
}

docker_base_environment = {
    "DECRYPTED_SETTINGS": "pupa_settings.py",
    "DESTINATION_SETTINGS": "pupa_settings.py",
    "DATABASE_URL": LA_METRO_DATABASE_URL,  # For use by entrypoint
    "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,  # For use in scraping scripts
    "LA_METRO_STAGING_DATABASE_URL": LA_METRO_STAGING_DATABASE_URL,
    "RPM": 60,
    "SENTRY_ENVIRONMENT": ENVIRONMENT,
}

with DAG(
    "full_scrape",
    default_args=default_args,
    schedule_interval="5 4 * * 0-5",
    description=(
        'Scrape all people and committees, bills, and events "politely" – that '
        "is, with requests throttled to 60 per minute, or 1 per second. This "
        "generally takes 6-7 hours."
    ),
) as dag:
    scrape_people_orgs_environment = docker_base_environment.copy()
    scrape_people_orgs_environment["TARGET"] = "people"

    person_scrape = BlackboxDockerOperator(
        task_id="scrape_people_orgs",
        environment=scrape_people_orgs_environment,
        **default_docker_args
    )

    scrape_events_environment = docker_base_environment.copy()
    scrape_events_environment["TARGET"] = "events"

    event_scrape = BlackboxDockerOperator(
        task_id="scrape_events",
        environment=scrape_events_environment,
        **default_docker_args
    )

    scrape_bills_environment = docker_base_environment.copy()
    scrape_bills_environment.update(
        {
            "TARGET": "bills",
            "WINDOW": 0,
        }
    )

    bill_scrape = BlackboxDockerOperator(
        task_id="scrape_bills",
        environment=scrape_bills_environment,
        **default_docker_args
    )

    person_scrape >> event_scrape >> bill_scrape
