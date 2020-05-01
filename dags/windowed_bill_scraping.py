import subprocess

from datetime import datetime, timedelta

from airflow import DAG
from base import DjangoOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'windowed_bill_scraping',
    default_args=default_args,
    schedule_interval=None # Eventually 5,20,35,50 * * * 0-6
)

def windowed_bill_scraping():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 35,50 minutes
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9 and now.minute < 35:
        pass
    elif now.weekday == 6 and now.hour <= 5 and now.minute < 35:
        pass
    else:
        # 5,20,35,50 datamade /usr/bin/flock -n /tmp/metrobills.lock -c "WINDOW=0.05 $APPDIR/scripts/lametro/windowed-bill-scrape.sh" >> /tmp/lametro.log
        subprocess.run('$APPDIR/scripts/lametro/windowed-bill-scrape.sh', capture_output=True)


t1 = DjangoOperator(
    task_id='windowed_bill_scraping',
    dag=dag,
    python_callable=windowed_bill_scraping
)
