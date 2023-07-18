from datetime import timedelta

from airflow import DAG

from constants import (
    LA_METRO_DATABASE_URL,
    LA_METRO_SEARCH_URL,
    START_DATE,
)
from operators.blackbox_docker_operator import TaggedDockerOperator


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=10),
    "image": "ghcr.io/metro-records/la-metro-councilmatic",
    "environment": {
        "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,
        "DATABASE_URL": LA_METRO_DATABASE_URL,
        "SEARCH_URL": LA_METRO_SEARCH_URL,
    },
}

with DAG(
    "tag_analytics",
    default_args=default_args,
    schedule_interval="0 0 1 * *",
    description="Generates analytics for Metro agenda tags and uploads a CSV file to Google Drive",
) as dag:
    t1 = TaggedDockerOperator(
        task_id="generate_tag_analytics",
        command="python manage.py generate_tag_analytics",
    )
