from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Use backported operator containing bug fix:
# - https://github.com/apache/airflow/issues/8629#issuecomment-641461423
# - https://pypi.org/project/apache-airflow-backport-providers-docker/
from airflow.providers.docker.operators.docker import DockerOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=15),
}

LA_METRO_DIR_PATH = os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/')
LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')
LA_METRO_SOLR_URL = os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro')

# Configure DAG container to connect to specific Docker network, useful for
# local development (not necessary in production)
DOCKER_NETWORK = os.getenv('DOCKER_NETWORK', None)

# Configure the location of the GPG keyring to mount into the container for
# decrypting secrets
GPG_KEYRING_PATH = os.getenv('GPG_KEYRING_PATH', '/home/datamade/.gnupg')

# Configure the Airflow directory path. For local development, this should
# be the root directory of your Airflow project. This has to be configured
# because the Docker daemon creates containers from the host, not from within
# the application container.
AIRFLOW_DIR_PATH = os.getenv(
    'AIRFLOW_DIR_PATH',
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)

print('\n'.join([AIRFLOW_DIR_PATH, GPG_KEYRING_PATH]))

with DAG('dockerized_update_index', default_args=default_args, schedule_interval='0 1 * * *') as dag:

    t1 = DockerOperator(
        task_id='update_index',
        image='datamade/la-metro-councilmatic:staging',
        command="/bin/bash -ce 'airflow_scripts/concat_settings.sh; python manage.py update_index --batch-size=100 --age=7'",
        environment={
            'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,
            'LA_METRO_SOLR_URL': LA_METRO_SOLR_URL,
        },
        volumes=[
            '{}:/root/.gnupg'.format(GPG_KEYRING_PATH),
            '{}:/app/airflow_configs'.format(os.path.join(AIRFLOW_DIR_PATH, 'configs')),
            '{}:/app/airflow_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'scripts'))
        ],
        network_mode=DOCKER_NETWORK,
    )
