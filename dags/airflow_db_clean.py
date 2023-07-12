"""
A maintenance workflow to clean old metadata from the Airflow database.
"""

from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

from constants import START_DATE

# Delete logs more than 30 days old
DELETE_BEFORE = datetime.now() - timedelta(days=30)

bash_command = f"airflow db clean -y --clean-before-timestamp '{DELETE_BEFORE}'"

with DAG(
    dag_id="airflow_db_cleanup",
    start_date=START_DATE,
    schedule="@monthly",
):
    BashOperator(task_id="task", bash_command=bash_command)
