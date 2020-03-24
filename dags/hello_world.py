from datetime import datetime, timedelta

import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args = {
    'start_date': datetime.now() - timedelta(days=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'hello_world',
    default_args=default_args,
    schedule_interval=None
)

def print_phrase():
    breakpoint()
    print("Hello, world")


t1 = PythonOperator(
    task_id='print_phrase',
    dag=dag,
    python_callable=print_phrase
)

t1
