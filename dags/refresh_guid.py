import sys

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator
from django.core.management import call_command

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'guid_log',
    default_args=default_args,
    schedule_interval='@daily'
)

APPDIR = '/home/datamade/lametro'
PYTHONDIR = '/home/datamade/.virtualenvs/lametro/bin/python'

def refresh_guid():
    call_command('refresh_guid')


t1 = DjangoOperator(
    task_id='refresh_guid',
    dag=dag,
    python_callable=refresh_guid
)

# 0 1 * * * datamade cd $APPDIR && $PYTHONDIR manage.py refresh_guid >> /var/log/councilmatic/lametro-refreshguid.log 2&1


#########

# 10,25,40 * * * * datamade /usr/bin/flock -n /tmp/lametro_dataload.lock -c 'cd $APPDIR && $PYTHONDIR manage.py refresh_pic >> /var/log/councilmatic/lametro-refreshpic.log 2>&1 && $PYTHONDIR manage.py compile_pdfs >> /var/log/councilmatic/lametro-compilepdfs.log 2>&1 && $PYTHONDIR manage.py convert_attachment_text >> /var/log/councilmatic/lametro-convertattachments.log 2>&1 && $PYTHONDIR manage.py update_index --batch-size=100 --age=1 >> /var/log/councilmatic/lametro-updateindex.log 2>&1 && $PYTHONDIR manage.py data_integrity >> /var/log/councilmatic/lametro-integrity.log 2>&1'

# Once per hour! Run the full data-import process,
# but remove the `age` argument from `update_index,`
# in order to update the entire Solr index.
# 55 * * * * datamade /usr/bin/flock -n /tmp/lametro_dataload.lock -c 'cd $APPDIR && $PYTHONDIR manage.py refresh_pic >> /var/log/councilmatic/lametro-refreshpic.log 2>&1 && $PYTHONDIR manage.py compile_pdfs >> /var/log/councilmatic/lametro-compilepdfs.log 2>&1 && $PYTHONDIR manage.py convert_attachment_text >> /var/log/councilmatic/lametro-convertattachments.log 2>&1 && $PYTHONDIR manage.py update_index --batch-size=100 >> /var/log/councilmatic/lametro-updateindex.log 2>&1 && $PYTHONDIR manage.py data_integrity >> /var/log/councilmatic/lametro-integrity.log 2>&1'

# /etc/cron.d/lametro-crontasks

# ordering