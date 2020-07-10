from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.docker_base import GPGDockerOperator


LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')
LA_METRO_SOLR_URL = os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro')

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15),
    'image': 'datamade/la-metro-councilmatic:staging',
    'environment': {
        'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
        'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
    },
}

with DAG('dockerized_update_index', default_args=default_args, schedule_interval='0 1 * * *') as dag:

    t1 = GPGDockerOperator(
        task_id='refresh_pic',
        command='python manage.py refresh_pic',
    )

    t2 = GPGDockerOperator(
        task_id='compile_pdfs',
        command='python manage.py compile_pdfs',
    )

    t3 = GPGDockerOperator(
        task_id='convert_attachment_text',
        command='python manage.py convert_attachment_text',
    )

    if datetime.now().minute <= 55:
        update_index_command = 'python manage.py update_index --batch-size=100'
    else:
        update_index_command = 'python manage.py update_index --batch-size=100 --age=1'

    t4 = GPGDockerOperator(
        task_id='update_index',
        command=update_index_command,
    )

    t5 = GPGDockerOperator(
        task_id='data_integrity',
        command='python manage.py data_integrity',
    )

    t1 >> t2 >> t3 >> t4 >> t5
