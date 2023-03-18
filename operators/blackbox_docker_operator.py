from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.exceptions import AirflowException

# Use backported operator containing bug fix:
# - https://github.com/apache/airflow/issues/8629#issuecomment-641461423
# - https://pypi.org/project/apache-airflow-backport-providers-docker/
from airflow.providers.docker.operators.docker import DockerOperator

from dags.constants import DOCKER_NETWORK, GPG_KEYRING_PATH, AIRFLOW_DIR_PATH, \
    LA_METRO_DOCKER_IMAGE_TAG


class BlackboxDockerOperator(DockerOperator):

    DEFAULT_VOLUMES = [
        '{}:/root/.gnupg'.format(GPG_KEYRING_PATH),
        '{}:/app/airflow_configs'.format(os.path.join(AIRFLOW_DIR_PATH, 'configs')),
        '{}:/app/airflow_scripts'.format(os.path.join(AIRFLOW_DIR_PATH, 'scripts')),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Append appropriate tag to specified image
        self.image = '{image}:{tag}'.format(
            image=self.image,
            tag=kwargs.get('tag', LA_METRO_DOCKER_IMAGE_TAG)
        )

        if not self.network_mode:  # Give DAG-configured network precedence
            self.network_mode = DOCKER_NETWORK

        self.force_pull = True
        self.auto_remove = True
        self.volumes = list(set(self.DEFAULT_VOLUMES + self.volumes))

        if not all(k in self.environment for k in ('DECRYPTED_SETTINGS', 'DESTINATION_SETTINGS')):
            raise ValueError('Must set DECRYPTED_SETTINGS and DESTINATION_SETTINGS environment variables')

        self.command = '/bin/bash -ce "airflow_scripts/concat_settings.sh; {}"'.format(self.command)
