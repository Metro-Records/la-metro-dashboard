import os
from flask_appbuilder.security.manager import AUTH_DB
from security import CustomManager

from airflow.configuration import conf

basedir = os.path.abspath(os.path.dirname(__file__))

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = conf.get('database', 'SQL_ALCHEMY_CONN')

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Custom security manager to redirect logins
AUTH_TYPE = AUTH_DB
SECURITY_MANAGER_CLASS = CustomManager
