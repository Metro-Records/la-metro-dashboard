from datetime import timedelta

from airflow import DAG

from constants import (
    LA_METRO_DATABASE_URL,
    LA_METRO_SOLR_URL,
    LA_METRO_DOCKER_IMAGE_TAG,
    LA_METRO_STAGING_DATABASE_URL,
    START_DATE,
)
from operators.blackbox_docker_operator import BlackboxDockerOperator


if LA_METRO_DOCKER_IMAGE_TAG == "master":
    deployment = "staging"
else:
    deployment = "production"

docker_base_environment = {
    "DECRYPTED_SETTINGS": "pupa_settings.py",
    "DESTINATION_SETTINGS": "pupa_settings.py",
    # For use by entrypoint
    "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,
    # For use in scraping scripts
    "DATABASE_URL": LA_METRO_DATABASE_URL,
    "LA_METRO_STAGING_DATABASE_URL": LA_METRO_STAGING_DATABASE_URL,
    "RPM": 60,
}

default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=15),
    "image": "ghcr.io/metro-records/scrapers-lametro",
    "environment": {
        "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,
        "LA_METRO_SOLR_URL": LA_METRO_SOLR_URL,
        "DECRYPTED_SETTINGS": f"configs/settings_deployment.{deployment}.py",
        "DESTINATION_SETTINGS": "councilmatic/settings_deployment.py",
    },
}

with DAG(
    "clean_stale_db_objects",
    default_args=default_args,
    schedule_interval="0 0 * * 0",
    description="Deletes objects from the database that have not"
    "been seen in a recent scrape",
) as dag:

    BlackboxDockerOperator(
        task_id="clean_stale_db_objects",
        environment=docker_base_environment,
        command="pupa clean --noinput",
    )
