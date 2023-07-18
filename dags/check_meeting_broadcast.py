from datetime import timedelta

from airflow import DAG

from constants import (
    LA_METRO_DATABASE_URL,
    LA_METRO_SEARCH_URL,
    START_DATE,
    LA_METRO_IMAGE_URL
)
from operators.blackbox_docker_operator import TaggedDockerOperator


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=1),
    "image": LA_METRO_IMAGE_URL,
    "environment": {
        "DATABASE_URL": LA_METRO_DATABASE_URL,
        "SEARCH_URL": LA_METRO_SEARCH_URL,
    },
}

with DAG(
    "check_meeting_broadcast",
    default_args=default_args,
    schedule_interval="*/10 * * * *",
    description="Mark live meeting as having been broadcast.",
) as dag:
    t1 = TaggedDockerOperator(
        task_id="check_current_meeting",
        command="python manage.py check_current_meeting",
    )
