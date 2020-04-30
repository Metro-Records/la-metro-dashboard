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

def daily_scraping():
    if datetime.today().weekday == 5:
        # 5 0 * * 5 datamade $APPDIR/scripts/lametro/person-scrape.sh >> /tmp/lametro.log
        subprocess.run("/la-metro-councilmatic/scripts/lametro/person-scrape.sh", capture_output=True)
    else:
        # 5 0 * * 0-4,6 datamade /usr/bin/flock /tmp/metrobills.lock /usr/bin/flock /tmp/metroevents.lock $APPDIR/scripts/lametro/full-scrape.sh >> /tmp/lametro.log
        subprocess.run("/la-metro-councilmatic/scripts/lametro/full-scrape.sh")

t1 = DjangoOperator(
    task_id='daily_scraping',
    dag=dag,
    python_callable=daily_scraping
)
