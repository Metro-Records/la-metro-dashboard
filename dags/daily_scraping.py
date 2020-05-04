import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'daily_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 5 0 * * 0-6
)

def run(cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print('Command: %s' % e.cmd)
        raise(e)

def daily_scraping():
    if datetime.today().weekday == 5:
        run("/scrapers-us-municipal/scripts/lametro/person-scrape.sh")
    else:
        run("/scrapers-us-municipal/scripts/lametro/full-scrape.sh")


t1 = DjangoOperator(
    task_id='daily_scraping',
    dag=dag,
    python_callable=daily_scraping
)
