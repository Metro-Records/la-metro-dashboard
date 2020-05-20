import os

from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser


if __name__ == '__main__':
    user = PasswordUser(models.User())
    user.username = os.environ['AIRFLOW_USERNAME']
    user.password = os.environ['AIRFLOW_PASSWORD']
    session = settings.Session()
    session.add(user)
    session.commit()
    session.close()
