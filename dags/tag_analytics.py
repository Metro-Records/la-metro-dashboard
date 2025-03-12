from datetime import timedelta

from airflow import DAG
from airflow.models import Variable

from constants import (
    LA_METRO_IMAGE_URL,
    LA_METRO_DATABASE_URL,
    LA_METRO_SEARCH_URL,
    START_DATE,
    LA_METRO_CONFIGS,
    ENVIRONMENT,
)
from operators.blackbox_docker_operator import TaggedDockerOperator


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=20),
    "image": LA_METRO_IMAGE_URL,
    "environment": {
        **LA_METRO_CONFIGS,
        "DATABASE_URL": LA_METRO_DATABASE_URL,
        "SEARCH_URL": LA_METRO_SEARCH_URL,
        "SENTRY_ENVIRONMENT": ENVIRONMENT,
        "GOOGLE_SERVICE_ACCT_API_KEY": Variable.get("google_service_acct_api_key"),
        "REMOTE_ANALYTICS_FOLDER": Variable.get("remote_analytics_folder")
    },
}

with DAG(
    "tag_analytics",
    catchup=False,
    default_args=default_args,
    schedule_interval="0 0 1 * *",
    description="Generates analytics for Metro agenda tags and"
    "uploads a CSV file to Google Drive",
) as dag:
    t1 = TaggedDockerOperator(
        task_id="generate_tag_analytics",
        command="python manage.py generate_tag_analytics",
    )
