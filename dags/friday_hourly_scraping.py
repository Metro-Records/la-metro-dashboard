import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'friday_hourly_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,5 21-23 * * 5
)

def friday_hourly_scraping():
    if datetime.now().minute < 5:
        # 0 21-23 * * 5 datamade /usr/bin/flock -n /tmp/metroevents.lock -c $APPDIR/scripts/lametro/fast-full-event-scrape.sh >> /tmp/lametro.log
        print("on the hour, full event scrape")
        subprocess.run('$APPDIR/scripts/lametro/fast-full-event-scrape.sh', capture_output=True)
    elif datetime.now().minute >= 5:
        # 5 21-23 * * 5 datamade /usr/bin/flock -n /tmp/metrobills.lock -c $APPDIR/scripts/lametro/fast-full-bill-scrape.sh >> /tmp/lametro.log
        print("5past hour, full bill scrape")
        subprocess.run('$APPDIR/scripts/lametro/fast-full-bill-scrape.sh', capture_output=True)



t1 = DjangoOperator(
    task_id='friday_hourly_scraping',
    dag=dag,
    python_callable=friday_hourly_scraping
)
