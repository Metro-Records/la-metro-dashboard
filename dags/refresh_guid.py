from datetime import timedelta

from airflow import DAG

from constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, START_DATE, ENVIRONMENT
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=5),
    "image": "ghcr.io/metro-records/la-metro-councilmatic",
    "environment": {
        "LA_METRO_DATABASE_URL": LA_METRO_DATABASE_URL,
        "LA_METRO_SOLR_URL": LA_METRO_SOLR_URL,
        "DECRYPTED_SETTINGS": "configs/settings_deployment.{}.py".format(ENVIRONMENT),
        "DESTINATION_SETTINGS": "councilmatic/settings_deployment.py",
    },
}

with DAG(
    "refresh_guid",
    default_args=default_args,
    schedule_interval="0 1 * * *",
    description="Sync Metro subjects with SmartLogic terms once nightly. Only used on staging.",
) as dag:
    t1 = BlackboxDockerOperator(
        task_id="refresh_guid",
        command="python manage.py refresh_guid",
    )
