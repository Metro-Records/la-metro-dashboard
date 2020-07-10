from datetime import datetime, timedelta
import os

from airflow import DAG

from dags.docker_base import GPGDockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15),
}

LA_METRO_DIR_PATH = os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/')
LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')
LA_METRO_SOLR_URL = os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro')

with DAG('dockerized_update_index', default_args=default_args, schedule_interval='0 1 * * *') as dag:

    t1 = GPGDockerOperator(
        task_id='update_index',
        image='datamade/la-metro-councilmatic:staging',
        command="python manage.py update_index --batch-size=100 --age=90",
        environment={
            'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
            'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        },
    )
