from datetime import timedelta

from airflow.decorators import dag, task

from constants import (
    LA_METRO_DATABASE_URL,
    LA_METRO_SEARCH_URL,
    LA_METRO_DOCKER_IMAGE_TAG,
    LA_METRO_STAGING_DATABASE_URL,
    START_DATE,
    LA_SCRAPERS_IMAGE_URL,
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
    "image": LA_SCRAPERS_IMAGE_URL,
    "environment": {
        "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,
        "SEARCH_URL": LA_METRO_SEARCH_URL,
        "DECRYPTED_SETTINGS": f"configs/settings_deployment.{deployment}.py",
        "DESTINATION_SETTINGS": "councilmatic/settings_deployment.py",
    },
}


@dag(
    schedule_interval="0 0 * * 0",
    description="Deletes objects from the database that have not"
    "been seen in a recent scrape",
    default_args=default_args,
    params={"window": 7, "max": 25, "report": False},
)
def clean_stale_db_objects(window=7, max=25, report=False):
    @task
    def get_flags(**kwargs):
        if kwargs["params"]["report"]:
            return "--report"
        else:
            return f"--window={kwargs['params']['window']} --max={kwargs['params']['max']} --yes"

    flags = get_flags()

    pupa_clean = BlackboxDockerOperator(
        task_id="clean_stale_db_objects",
        environment=docker_base_environment,
        command=f"pupa clean {flags}",
    )

    flags >> pupa_clean


clean_stale_db_objects()
