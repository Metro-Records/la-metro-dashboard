import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'saturday_hourly_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,5 0-5 * * 0-6
)

def run(cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print('Command: %s' % e.output)
        raise(e)

def saturday_hourly_scraping():
    if datetime.now().minute < 5:
        print("on the hour, full event scrape")
        run('/scrapers-us-municipal/scripts/lametro/fast-full-event-scrape.sh')
    elif datetime.now().minute >= 5:
        print("5past hour, full bill scrape")
        run('/scrapers-us-municipal/scripts/lametro/fast-full-bill-scrape.sh')


t1 = DjangoOperator(
    task_id='saturday_hourly_scraping',
    dag=dag,
    python_callable=saturday_hourly_scraping
)
