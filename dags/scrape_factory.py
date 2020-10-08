import os

from airflow import DAG

from dags.config import SCRAPING_DAGS
from dags.constants import LA_METRO_DATABASE_URL, AIRFLOW_DIR_PATH, \
    DAG_DESCRIPTIONS, START_DATE
from operators.blackbox_docker_operator import BlackboxDockerOperator


docker_base_environment = {
    'DECRYPTED_SETTINGS': 'pupa_settings.py',
    'DESTINATION_SETTINGS': 'pupa_settings.py',
    'DATABASE_URL': LA_METRO_DATABASE_URL,  # For use by entrypoint
    'LA_METRO_DATABASE_URL': LA_METRO_DATABASE_URL,  # For use in scraping scripts
}

for dag_name, dag_config in SCRAPING_DAGS.items():
    for idx, interval in enumerate(dag_config['schedule_interval'], start=1):
        dag_id = dag_name if len(dag_config['schedule_interval']) == 1 else '{0}_{1}'.format(dag_name, idx)

        dag = DAG(
            dag_id,
            schedule_interval=interval,
            start_date=START_DATE,
            default_args={'execution_timeout': dag_config['execution_timeout']},
            description=DAG_DESCRIPTIONS.get(dag_name, 'tk')
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
