from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, \
    LA_METRO_DOCKER_IMAGE_TAG, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


deployment = 'staging' if LA_METRO_DOCKER_IMAGE_TAG == 'master' else 'production'

default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(minutes=10),
    'image': 'ghcr.io/Metro-Records/la-metro-councilmatic',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        'DECRYPTED_SETTINGS': 'configs/settings_deployment.{}.py'.format(deployment),
        'DESTINATION_SETTINGS': 'councilmatic/settings_deployment.py',
    },
}

with DAG(
    'tag_analytics',
    default_args=default_args,
    schedule_interval='0 0 1 * *',
    description='Generates analytics for Metro agenda tags and uploads a CSV file to Google Drive'
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='generate_tag_analytics',
        command='python manage.py generate_tag_analytics',
    )
