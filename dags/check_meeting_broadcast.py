from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, \
    LA_METRO_DOCKER_IMAGE_TAG, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(minutes=1),
    'image': 'ghcr.io/Metro-Records/la-metro-councilmatic',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        'DECRYPTED_SETTINGS': 'configs/settings_deployment.{}.py'.format(LA_METRO_DOCKER_IMAGE_TAG),
        'DESTINATION_SETTINGS': 'councilmatic/settings_deployment.py',
    },
}

with DAG(
    'check_meeting_broadcast',
    default_args=default_args,
    schedule_interval='*/10 * * * *',
    description='Mark live meeting as having been broadcast.',
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='check_current_meeting',
        command='python manage.py check_current_meeting',
        tag=LA_METRO_DOCKER_IMAGE_TAG,
    )
