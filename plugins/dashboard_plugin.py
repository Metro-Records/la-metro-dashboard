from datetime import datetime
import json

import os
import sys

from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from flask_appbuilder import BaseView, expose
import pytz
import requests


sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

PACIFIC_TIMEZONE = pytz.timezone('US/Pacific')
CENTRAL_TIMEZONE = pytz.timezone('US/Central')


class Dashboard(BaseView):
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    AIRFLOW_SESSION = settings.Session()

    def get_dags(self):
        latest_dagruns = dagrun.DagRun.get_latest_runs(self.AIRFLOW_SESSION)

        event_dags = []
        bill_dags = []

        for dr in latest_dagruns:
            current_dag = bag.get_dag(dr.dag_id)

            for ti in dr.get_task_instances():
                if 'event' in ti.task_id:
                    event_dags.append(current_dag)
                    break
                elif 'bill' in ti.task_id:
                    bill_dags.append(current_dag)
                    break
                elif 'daily' in ti.task_id:
                    event_dags.append(current_dag)
                    bill_dags.append(current_dag)
                    break

        return event_dags, bill_dags

    def get_last_successful_run(self, dags):
        successful_runs = []

        for dag in dags:
            last_successful_run = self.get_last_successful_run(dag.dag_id, self.AIRFLOW_SESSION)

            if last_successful_run:
                successful_runs.append(last_successful_run)

        successful_runs.sort(key=lambda x: x.end_date, reverse=True)
        last_run, last_run_time = self.get_run_info(successful_runs)

        return last_run, last_run_time

    def get_next_scheduled_run(self, runs):
        runs.sort(key=lambda x: x['next_scheduled']['pst_time'], reverse=True)

        if len(runs) > 0:
            return runs[0]
        else:
            return None

    def get_dag_ids(self, dags):
        return [getattr(dag, 'dag_id') for dag in dags]

    @expose('/')
    def list(self):
        dag_info = self.get_dag_info(self.AIRFLOW_SESSION)

        event_dags, bill_dags = self.get_dags()

        event_last_run, event_last_run_time = self.get_last_successful_run(event_dags)
        bill_last_run, bill_last_run_time = self.get_last_successful_run(bill_dags)

        event_next_runs = [dag for dag in dag_info if dag['name'] in self.get_dag_ids(event_dags)]
        event_next_run = self.get_next_scheduled_run(event_next_runs)

        bill_next_runs = [dag for dag in dag_info if dag['name'] in self.get_dag_ids(bill_dags)]
        bill_next_run = self.get_next_scheduled_run(bill_next_runs)

        events_in_db, bills_in_db, bills_in_index = self.get_db_info()

        metadata = {
            'data': dag_info,
            'event_last_run': event_last_run,
            'event_last_run_time': event_last_run_time,
            'event_next_run': event_next_run,
            'events_in_db': events_in_db,
            'bill_last_run': bill_last_run,
            'bill_last_run_time': bill_last_run_time,
            'bill_next_run': bill_next_run,
            'bills_in_db': bills_in_db,
            'bills_in_index': bills_in_index,
        }

        return self.render_template('dashboard.html', **metadata)

    def get_dag_info(self, session):
        bag = DagBag()

        dags = [bag.get_dag(dag_id) for dag_id in bag.dag_ids
                if not dag_id.startswith('airflow_')]  # Filter meta-DAGs

        data = []

        for d in dags:
            last_run = dag.get_last_dagrun(d.dag_id, session, include_externally_triggered=True)

            if last_run:
                run_state = last_run.get_state()

                run_date = last_run.execution_date

                pst_run_time = run_date.astimezone(PACIFIC_TIMEZONE)
                cst_run_time = run_date.astimezone(CENTRAL_TIMEZONE)
                run_date_info = {
                    'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                    'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
                }

                now = datetime.now(pytz.utc)
                next_scheduled = d.following_schedule(now)

                pst_next_scheduled = next_scheduled.astimezone(PACIFIC_TIMEZONE)
                cst_next_scheduled = next_scheduled.astimezone(CENTRAL_TIMEZONE)
                next_scheduled_info = {
                    'pst_time': datetime.strftime(pst_next_scheduled, "%m/%d/%y %I:%M %p"),
                    'cst_time': datetime.strftime(cst_next_scheduled, "%m/%d/%y %I:%M %p")
                }
            else:
                run_state = None
                run_date_info = None
                next_scheduled_info = None

            dag_info = {
                'name': d.dag_id,
                'description': d.description,
                'run_state': run_state,
                'run_date': run_date_info,
                'next_scheduled': next_scheduled_info
            }

            data.append(dag_info)

        return data

    def get_db_info(self):
        url_parts = {
            'hostname': os.getenv('LA_METRO_HOST', 'http://app:8000'),
            'api_key': os.getenv('LA_METRO_API_KEY', 'test key'),
        }

        endpoint = '{hostname}/object-counts/{api_key}'.format(**url_parts)

        response = requests.get(endpoint)

        try:
            response_json = response.json()

        except json.decoder.JSONDecodeError:
            print(response.text)

        else:
            if response_json['status_code'] == 200:
                return (response_json['event_count'],
                        response_json['bill_count'],
                        response_json['search_index_count'])

        return None, None, None

    def get_run_info(self, runs):
        if len(runs) > 0:
            run = runs[0]
            run_date = run.execution_date

            pst_run_time = run_date.astimezone(PACIFIC_TIMEZONE)
            cst_run_time = run_date.astimezone(CENTRAL_TIMEZONE)

            run_time = {
                'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
            }
        else:
            run = None
            run_time = None

        return (run, run_time)

    def get_last_successful_run(self, dag_id, self.AIRFLOW_SESSION):
        """
        Given a DAG ID and a SQLAlchemy Session object, return the last successful
        DagRun.
        """
        return self.AIRFLOW_SESSION.query(dagrun.DagRun)\
                      .filter(dagrun.DagRun.dag_id == dag_id)\
                      .filter(dagrun.DagRun.state == 'success')\
                      .order_by(dagrun.DagRun.execution_date.desc())\
                      .first()


dashboard_package = {
    'name': 'Dashboard View',
    'category': 'Dashboard Plugin',
    'view': Dashboard()
}


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    appbuilder_views = [dashboard_package]
