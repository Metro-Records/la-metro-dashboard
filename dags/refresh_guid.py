from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, \
    LA_METRO_DOCKER_IMAGE_TAG, DAG_DESCRIPTIONS, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': START_DATE,
    'execution_timeout': timedelta(minutes=5),
    'image': 'datamade/la-metro-councilmatic',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        'DECRYPTED_SETTINGS': 'configs/settings_deployment.{}.py'.format(LA_METRO_DOCKER_IMAGE_TAG),
        'DESTINATION_SETTINGS': 'councilmatic/settings_deployment.py',
    },
}

with DAG(
    'refresh_guid',
    default_args=default_args,
    schedule_interval='0 1 * * *',
    description=DAG_DESCRIPTIONS['refresh_guid']
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='refresh_guid',
        command='python manage.py refresh_guid',
    )
