import os

from airflow import DAG
from croniter import croniter

from dags.config import SCRAPING_DAGS
from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
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
            task = BlackboxDockerOperator(
                task_id='scrape',
                image='datamade/scrapers-us-municipal',
                volumes=[
                    '{}:/app/scraper_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'dags', 'scripts'))
                ],
                command=dag_config['command'],
                environment=docker_environment
            )

        globals()[dag_id] = dag

        seen_ids.append(dag_id)
