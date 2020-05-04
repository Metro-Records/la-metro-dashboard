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

def run(cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print('Command: %s' % e.cmd)
        raise(e)

def windowed_bill_scraping():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 35,50 minutes
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9 and now.minute < 35:
        pass
    elif now.weekday == 6 and now.hour <= 5 and now.minute < 35:
        pass
    else:
        run('/scrapers-us-municipal/scripts/lametro/windowed-bill-scrape.sh')


t1 = DjangoOperator(
    task_id='windowed_bill_scraping',
    dag=dag,
    python_callable=windowed_bill_scraping
)
