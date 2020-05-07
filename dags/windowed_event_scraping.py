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
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9 and now.minute < 30:
        return 'no_scrape'
    elif now.weekday == 6 and now.hour <= 5 and now.minute < 30:
        return 'no_scrape'
    else:
        return 'windowed_event_scraping'


branch = BranchPythonOperator(
    task_id='handle_scheduling',
    dag=dag,
    python_callable=handle_scheduling
)

windowed_event_scraping = BashOperator(
    task_id='windowed_event_scraping',
    dag=dag,
    bash_command='/app/scripts/windowed-event-scrape.sh '
)

no_scrape = DummyOperator(
    task_id='no_scrape',
    dag=dag
)

branch >> [windowed_event_scraping, no_scrape]
