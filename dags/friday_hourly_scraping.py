import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
# from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=60)
}

dag = DAG(
    'friday_hourly_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,5 21-23 * * 5
)

def run(cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print('Command: %s' % e.output)
        raise(e)

def friday_hourly_scraping():
    if datetime.now().minute < 5:
        print("on the hour, full event scrape")
        run('/app/scripts/fast-full-event-scrape.sh')
    elif datetime.now().minute >= 5:
        print("5past hour, full bill scrape")
        run('/app/scripts/fast-full-bill-scrape.sh')


t1 = PythonOperator(
    task_id='friday_hourly_scraping',
    dag=dag,
    python_callable=friday_hourly_scraping
)
