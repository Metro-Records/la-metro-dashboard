from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin

import os

"""
Create this file as ./plugins/staticfiles.py in your ARIFLOW_HOME directory
It will serve all files under ./static/ available under /a/static/ (The "a" comes from the ``url_prefix`` argument.)
"""


bp = Blueprint(
    "test_plugin", __name__,
    url_prefix="/a",
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')),
    static_url_path='/static')


class StaticPlugin(AirflowPlugin):
    name = "themes"
    flask_blueprints = [bp]