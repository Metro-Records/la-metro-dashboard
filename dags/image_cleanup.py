from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

from dags.constants import START_DATE


with DAG(
    'image_cleanup',
    schedule_interval='0 12 * * *',
    start_date=START_DATE,
    description='Prune Docker images every day at noon.'
) as dag:

    image_cleaup = BashOperator(
        task_id='prune_images',
        bash_command='docker image prune -f'
    )
