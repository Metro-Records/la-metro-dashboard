import os

from airflow import DAG
from airflow.models import TaskInstance
from airflow.operators.python_operator import ShortCircuitOperator
from airflow.utils.db import provide_session

from croniter import croniter
from docker.types import Mount

from dags.config import SCRAPING_DAGS
from dags.constants import LA_METRO_DATABASE_URL, LA_METRO_STAGING_DATABASE_URL, \
    AIRFLOW_DIR_PATH, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
    'LA_METRO_STAGING_DATABASE_URL': LA_METRO_STAGING_DATABASE_URL,
    'OCD_DIVISION_CSV': '/app/configs/lametro_divisions.csv',
}

def get_dag_id(dag_name, dag_config, interval):
    '''
    Generate a unique ID from the DAG name and interval. This works because
    we only have one interval per day (or range of days). The DAG creation loop
    contains some logic to catch duplicate IDs, in case this is ever not the
    case. If that error occurs, this method will need to be updated.
    '''
    if len(dag_config['schedule_interval']) == 1:
        return dag_name

    # See https://github.com/kiorky/croniter/blob/master/src/croniter/croniter.py
    c = croniter(interval)

    # {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}
    int_day_map = {v: k for k, v in c.ALPHACONV[4].items()}

    *_, days = croniter(interval).expanded

    if len(days) == 1:
        return '{0}_{1}'.format(dag_name, int_day_map[days[0]])

    else:
        return '{0}_{1}_thru_{2}'.format(dag_name, int_day_map[days[0]], int_day_map[days[-1]])

@provide_session
def previous_scrape_done(session=None, **kwargs):
    running_scrapes = session.query(TaskInstance).filter(
        TaskInstance.dag_id == kwargs['dag'].dag_id,
        TaskInstance.task_id == 'scrape',
        TaskInstance.start_date < kwargs['execution_date'],
        TaskInstance.state == 'running'
    )

    return running_scrapes.count() == 0

seen_ids = []

for dag_name, dag_config in SCRAPING_DAGS.items():
    for interval in dag_config['schedule_interval']:
        dag_id = get_dag_id(dag_name, dag_config, interval)

        try:
            assert dag_id not in seen_ids
        except AssertionError:
            raise AssertionError('DAG with ID {} already exists. \
                Is there more than one schedule interval for the same day?')

        dag = DAG(
            dag_id,
            schedule_interval=interval,
            default_args={
                'start_date': START_DATE,
                'execution_timeout': dag_config['execution_timeout']
            },
            description=dag_config['description']
        )

        docker_environment = docker_base_environment.copy()
        docker_environment.update(dag_config['docker_environment'])

        with dag:
            check_previous = ShortCircuitOperator(
                task_id='check_previous',
                python_callable=previous_scrape_done,
                provide_context=True
            )

            scrape = BlackboxDockerOperator(
                task_id='scrape',
                image='ghcr.io/metro-records/scrapers-lametro',
                mounts=[
                    Mount(
                        source=os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'),
                        target='/app/scraper_scripts',
                        type='bind',
                    ),
                    Mount(
                        source=os.path.join(AIRFLOW_DIR_PATH, 'configs'),
                        target='/app/configs',
                        type='bind',
                    ),
                ],
                command=dag_config['command'],
                environment=docker_environment,
            )

            check_previous >> scrape

        globals()[dag_id] = dag

        seen_ids.append(dag_id)
