import os

from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

from constants import (
    DOCKER_NETWORK,
    GPG_KEYRING_PATH,
    AIRFLOW_DIR_PATH,
)


class TaggedDockerOperator(DockerOperator):
    DEFAULT_VOLUMES = [
        (GPG_KEYRING_PATH, "/root/.gnupg"),
        (os.path.join(AIRFLOW_DIR_PATH, "configs"), "/app/airflow_configs"),
        (os.path.join(AIRFLOW_DIR_PATH, "scripts"), "/app/airflow_scripts"),
    ]

    MOUNTS = [
            Mount(target, source, type="bind") for source, target in DEFAULT_VOLUMES
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.network_mode:  # Give DAG-configured network precedence
            self.network_mode = DOCKER_NETWORK

        self.force_pull = True
        self.auto_remove = "force"

        self.mount_tmp_dir = False
        self.mounts = list(self.mounts + self.MOUNTS)


class BlackboxDockerOperator(TaggedDockerOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = '/bin/bash -ce "blackbox_postdeploy; {}"'.format(
            self.command
        )
