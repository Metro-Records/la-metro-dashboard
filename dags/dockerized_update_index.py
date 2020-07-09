from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15)
}

LA_METRO_DIR_PATH = os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/')
LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')
LA_METRO_SOLR_URL = os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro')

# Configure DAG container to connect to specific Docker network, useful for
# local development (not necessary in production)
DOCKER_NETWORK = os.getenv('DOCKER_NETWORK', None)

with DAG('dockerized_update_index', default_args=default_args, schedule_interval='0 1 * * *') as dag:

    t1 = BashOperator(
        task_id='docker_build',
        bash_command='docker build {} -t lametro:latest'.format(LA_METRO_DIR_PATH)
    )

    t2 = DockerOperator(
        task_id='update_index',
        image='lametro:latest',
        command='python manage.py update_index --batch-size=100 --age=7',
        environment={
            'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
            'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        },
        network_mode=DOCKER_NETWORK
    )

    t1 >> t2