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

# def refresh_pic():
#     call_command('refresh_pic')

def compile_pdfs():
    call_command('compile_pdfs')

def convert_attachment_text():
    call_command('convert_attachment_text')

def update_index():
    if datetime.now().minute >= 55:
        call_command('update_index --batch-size=100')
    else:
        call_command('update_index --batch-size=100 --age=1')

def data_integrity():
    call_command('data_integrity')

#########

# t1 = DjangoOperator(
    # cd $APPDIR && $PYTHONDIR manage.py refresh_pic >> /var/log/councilmatic/lametro-refreshpic.log 2>&1 
#     task_id='refresh_pic',
#     dag=dag,
#     python_callable=refresh_pic
# )

t2 = DjangoOperator(
    # && $PYTHONDIR manage.py compile_pdfs >> /var/log/councilmatic/lametro-compilepdfs.log 2>&1 
    task_id='compile_pdfs',
    dag=dag,
    python_callable=compile_pdfs
)

t3 = DjangoOperator(
    # && $PYTHONDIR manage.py convert_attachment_text >> /var/log/councilmatic/lametro-convertattachments.log 2>&1 
    task_id='convert_attachment_text',
    dag=dag,
    python_callable=convert_attachment_text
)

t4 = DjangoOperator(
    # && $PYTHONDIR manage.py update_index --batch-size=100 --age=1 >> /var/log/councilmatic/lametro-updateindex.log 2>&1 
    # NOTE: on the 55min mark, don't include the age flag
    task_id='update_index',
    dag=dag,
    python_callable=update_index
)

t5 = DjangoOperator(
    # && $PYTHONDIR manage.py data_integrity >> /var/log/councilmatic/lametro-integrity.log 2>&1
    task_id='data_integrity',
    dag=dag,
    python_callable=data_integrity
)

t2 > t3 > t4 > t5
