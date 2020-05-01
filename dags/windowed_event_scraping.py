import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'windowed_event_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 0,15,30,45 * * * 0-6
)

def windowed_event_scraping():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 30,45 minutes
    if now.weekday == 5 and now.hour >= 9 and now.minute < 30:
        pass
    elif now.weekday == 6 and now.hour <= 5 and now.minute < 30:
        pass
    else:
        # 0,15,30,45 * * * 0-4 datamade /usr/bin/flock -n /tmp/metroevents.lock -c "WINDOW=0.05 $APPDIR/scripts/lametro/windowed-event-scrape.sh" >> /tmp/lametro.log
        subprocess.run('$APPDIR/scripts/lametro/windowed-bill-scrape.sh', capture_output=True)


t1 = DjangoOperator(
    task_id='windowed_event_scraping',
    dag=dag,
    python_callable=windowed_event_scraping
)
