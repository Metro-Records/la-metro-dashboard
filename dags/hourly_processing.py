import sys

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator
from django.core.management import call_command


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=5)
}

dag = DAG(
    'hourly_processing',
    default_args=default_args,
    schedule_interval=None # eventually '10,25,40,55 * * * * '
)

def refresh_pic():
    call_command('refresh_pic')

def compile_pdfs():
    call_command('compile_pdfs')

def convert_attachment_text():
    call_command('convert_attachment_text')

def update_index():
    if datetime.now().minute <= 55:
        call_command('update_index', batchsize=100)
    else:
        call_command('update_index', batchsize=100, age=1)

def data_integrity():
    call_command('data_integrity')


t1 = DjangoOperator(
    task_id='refresh_pic',
    dag=dag,
    python_callable=refresh_pic
)

t2 = DjangoOperator(
    task_id='compile_pdfs',
    dag=dag,
    trigger_rule='all_done',
    python_callable=compile_pdfs
)

t3 = DjangoOperator(
    task_id='convert_attachment_text',
    dag=dag,
    trigger_rule='all_done',
    python_callable=convert_attachment_text
)

t4 = DjangoOperator(
    task_id='update_index',
    dag=dag,
    trigger_rule='all_done',
    python_callable=update_index
)

t5 = DjangoOperator(
    task_id='data_integrity',
    dag=dag,
    trigger_rule='all_done',
    python_callable=data_integrity
)

t1 >> t2 >> t3 >> t4 >> t5
