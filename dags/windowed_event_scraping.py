from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator

from base import SCRAPERS_DIR_PATH, LA_METRO_DATABASE_URL

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=3)
}

dag = DAG(
    'windowed_event_scraping',
    default_args=default_args,
    schedule_interval='0,15,30,45 * * * 0-6',
    description=('Run an event scrape with a window of 0.05 at 0, 15, 30, and 45 minutes every hour. Between 9pm Friday and 6am Saturday UTC '
        '(2pm to 11pm Friday PST), run an event scrape with a window of 1 only at 30 and 45 minutes past the hour. '
        'Windowed event scrapes scrape events where specific dates are within the given window, '
        'or in the future. This generally takes somewhere between a few seconds and a few minutes, '
        'depending on the volume of updates.')
)

def handle_scheduling():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 30,45 minutes
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9:
        if now.minute < 30:
            return 'no_scrape'
        return 'larger_window_event_scraping'
        
    elif now.weekday == 6 and now.hour <= 5:
        if now.minute < 30:
            return 'no_scrape'
        return 'larger_window_event_scraping'

    return 'windowed_event_scraping'


branch = BranchPythonOperator(
    task_id='handle_scheduling',
    dag=dag,
    python_callable=handle_scheduling
)

windowed_event_scraping = BashOperator(
    task_id='windowed_event_scraping',
    dag=dag,
    params={
        'window': 0.05,
        'target': 'events',
        'rpm': 60,
        'scrapers_dir_path': SCRAPERS_DIR_PATH,
        'la_metro_database_url': LA_METRO_DATABASE_URL
    },
    bash_command='scripts/targeted-scrape.sh'
)

larger_window_event_scraping = BashOperator(
    task_id='larger_window_event_scraping',
    dag=dag,
    params={
        'window': 1,
        'target': 'events',
        'rpm': 60,
        'scrapers_dir_path': SCRAPERS_DIR_PATH,
        'la_metro_database_url': LA_METRO_DATABASE_URL
    },
    bash_command='scripts/targeted-scrape.sh'
)

no_scrape = DummyOperator(
    task_id='no_scrape',
    dag=dag
)

branch >> [windowed_event_scraping, larger_window_event_scraping, no_scrape]
