from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Use backported operator containing bug fix:
# - https://github.com/apache/airflow/issues/8629#issuecomment-641461423
# - https://pypi.org/project/apache-airflow-backport-providers-docker/
from airflow.providers.docker.operators.docker import DockerOperator


class BlackboxDockerOperator(DockerOperator):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Configure DAG container to connect to specific Docker network, useful for
        # local development (not necessary in production)
        DOCKER_NETWORK = os.getenv('DOCKER_NETWORK', None)

        if not self.network_mode:  # Give DAG-configured network precedence
            self.network_mode = DOCKER_NETWORK

        self.force_pull = True

        # Configure the location of the GPG keyring to mount into the container for
        # decrypting secrets
        GPG_KEYRING_PATH = os.getenv('GPG_KEYRING_PATH', '/home/datamade/.gnupg')

        # Configure the Airflow directory path. For local development, this should
        # be the root directory of your Airflow project. This has to be configured
        # because the Docker daemon creates containers from the host, not from within
        # the application container.
        AIRFLOW_DIR_PATH = os.getenv(
            'AIRFLOW_DIR_PATH',
            os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
        )

        self.volumes += [
            '{}:/root/.gnupg'.format(GPG_KEYRING_PATH),
            '{}:/app/airflow_configs'.format(os.path.join(AIRFLOW_DIR_PATH, 'configs')),
            '{}:/app/airflow_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'scripts'))
        ]

        # TODO: Is this safe? (In other words, can self.command be something
        # that would break this?)
        self.command = '/bin/bash -ce "airflow_scripts/concat_settings.sh; {}"'.format(self.get_command())
