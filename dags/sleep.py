from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'start_date': datetime.now() - timedelta(days=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'sleep',
    default_args=default_args,
    schedule_interval=None
)

t1 = BashOperator(
    task_id='sleep',
    dag=dag,
    bash_command='sleep 30'
)
