from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_SOLR_URL, DAG_DESCRIPTIONS
from operators.blackbox_docker_operator import BlackboxDockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15),
    'image': 'datamade/la-metro-councilmatic:staging',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        'DECRYPTED_SETTINGS': 'configs/settings_deployment.staging.py',
        'DESTINATION_SETTINGS': 'councilmatic/settings_deployment.py',
    },
}

with DAG(
    'hourly_processing',
    default_args=default_args,
    schedule_interval='10,25,40,55 * * * *',
    description=DAG_DESCRIPTIONS['hourly_processing']
) as dag:

    t1 = BlackboxDockerOperator(
        task_id='refresh_pic',
        command='python manage.py refresh_pic',
    )

    t2 = BlackboxDockerOperator(
        task_id='compile_pdfs',
        command='python manage.py compile_pdfs',
    )

    t3 = BlackboxDockerOperator(
        task_id='convert_attachment_text',
        command='python manage.py convert_attachment_text',
    )

    if datetime.now().minute <= 55:
        update_index_command = 'python manage.py update_index --batch-size=100'
    else:
        update_index_command = 'python manage.py update_index --batch-size=100 --age=1'

    t4 = BlackboxDockerOperator(
        task_id='update_index',
        command=update_index_command,
    )

    t5 = BlackboxDockerOperator(
        task_id='data_integrity',
        command='python manage.py data_integrity',
    )

    t1 >> t2 >> t3 >> t4 >> t5
