from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Use backported operator containing bug fix:
# - https://github.com/apache/airflow/issues/8629#issuecomment-641461423
# - https://pypi.org/project/apache-airflow-backport-providers-docker/
from airflow.providers.docker.operators.docker import DockerOperator

from dags.constants import DOCKER_NETWORK, GPG_KEYRING_PATH, AIRFLOW_DIR_PATH


class BlackboxDockerOperator(DockerOperator):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not self.network_mode:  # Give DAG-configured network precedence
            self.network_mode = DOCKER_NETWORK

        self.force_pull = True

        self.volumes += [
            '{}:/root/.gnupg'.format(GPG_KEYRING_PATH),
            '{}:/app/airflow_configs'.format(os.path.join(AIRFLOW_DIR_PATH, 'configs')),
            '{}:/app/airflow_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'scripts'))
        ]

        # TODO: Is this safe? (In other words, can self.command be something
        # that would break this?)
        self.command = '/bin/bash -ce "airflow_scripts/concat_settings.sh; {}"'.format(self.get_command())
