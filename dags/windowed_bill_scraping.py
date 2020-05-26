from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(hours=3)
}

dag = DAG(
    'windowed_bill_scraping',
    default_args=default_args,
    schedule_interval=None, # Eventually 5,20,35,50 * * * 0-6
    description=('Run a bill scrape with a window of 0.05. Between 9pm Friday and 6am Saturday '
        '(2pm to 11pm Friday PST), run a bill scrape with a window of 1 only at 35 and 50 minutes past the hour. '
        'Windowed bill scrapes scrape bills where specific dates are within the given window, '
        'or in the future. This generally takes somewhere between a few seconds and a few minutes, '
        'depending on the volume of updates.')
)

def handle_scheduling():
    # SUNDAY THROUGH SATURDAY
    # 9pm FRIDAY through 5am SATURDAY, only run at 35,50 minutes
    now = datetime.now()
    if now.weekday == 5 and now.hour >= 9:
        if now.minute < 35:
            return 'no_scrape'
        return 'larger_window_bill_scraping'

    elif now.weekday == 6 and now.hour <= 5:
        if now.minute < 35:
            return 'no_scrape'
        return 'larger_window_bill_scraping'

    return 'windowed_bill_scraping'


branch = BranchPythonOperator(
    task_id='handle_scheduling',
    dag=dag,
    python_callable=handle_scheduling
)

windowed_bill_scraping = BashOperator(
    task_id='windowed_bill_scraping',
    dag=dag,
    params={'window': 0.05, 'target': 'bills', 'rpm': 60},
    bash_command='scripts/targeted-scrape.sh'
)

larger_window_bill_scraping = BashOperator(
    task_id='larger_window_bill_scraping',
    dag=dag,
    params={'window': 1, 'target': 'bills', 'rpm': 60},
    bash_command='scripts/targeted-scrape.sh'
)

no_scrape = DummyOperator(
    task_id='no_scrape',
    dag=dag
)

branch >> [windowed_bill_scraping, larger_window_bill_scraping, no_scrape]
