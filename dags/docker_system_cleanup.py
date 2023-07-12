from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

from constants import START_DATE


with DAG(
    'docker_system_cleanup',
    schedule_interval='0 12 * * *',
    start_date=START_DATE,
    description='Prune Docker images, containers, and networks every day at noon. https://docs.docker.com/config/pruning/'
) as dag:

    docker_system_cleanup = BashOperator(
        task_id='prune_images',
        bash_command='docker system prune -f'
    )
