from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, DAG_DESCRIPTIONS
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=5),
    'image': 'datamade/la-metro-councilmatic:staging',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        'DECRYPTED_SETTINGS': 'configs/settings_deployment.staging.py',
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
