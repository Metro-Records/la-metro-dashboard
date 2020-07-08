from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator


LA_METRO_DIR_PATH = os.getenv('LA_METRO_DIR_PATH', '/la-metro-councilmatic/')

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

with DAG('dockerized_update_index', default_args=default_args, schedule_interval='0 1 * * *') as dag:

    t1 = BashOperator(
        task_id='docker_build',
        bash_command='docker build {} -t lametro:latest'.format(LA_METRO_DIR_PATH)
    )

    t2 = DockerOperator(
        task_id='update_index',
        image='lametro:latest',
        command='python manage.py update_index --batch-size=100'
    )

    t1 >> t2