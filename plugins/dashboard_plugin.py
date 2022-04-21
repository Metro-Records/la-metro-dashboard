from datetime import datetime
import json

import os
import sys

from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint, g, url_for, redirect
from flask_appbuilder import BaseView, expose, has_access
import pytz
import requests


sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

PACIFIC_TIMEZONE = pytz.timezone('US/Pacific')
CENTRAL_TIMEZONE = pytz.timezone('US/Central')


class Dashboard(BaseView):
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')

    DATETIME_FORMAT = '%m/%d/%y %I:%M %p'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.airflow_session = settings.Session()
        self.airflow_dag_bag = DagBag()

    @expose('/')
    @has_access
    def list(self):
        dag_info = self.get_dag_info()

        event_dags = [dag for dag in dag_info if 'event' in dag['name'] or dag['name'] == 'full_scrape']
        bill_dags = [dag for dag in dag_info if 'bill' in dag['name'] or dag['name'] == 'full_scrape']

        event_last_run = self.get_last_successful_dagrun(event_dags)
        bill_last_run = self.get_last_successful_dagrun(bill_dags)

        event_next_run = self.get_next_dagrun(event_dags)
        bill_next_run = self.get_next_dagrun(bill_dags)

        events_in_db, bills_in_db, bills_in_index = self.get_db_info()

        metadata = {
            'data': dag_info,
            'event_last_run': event_last_run,
            'event_next_run': event_next_run,
            'events_in_db': events_in_db,
            'bill_last_run': bill_last_run,
            'bill_next_run': bill_next_run,
            'bills_in_db': bills_in_db,
            'bills_in_index': bills_in_index,
            'datetime_format': self.DATETIME_FORMAT,
        }

        return self.render_template('dashboard.html', **metadata)

    def get_dag_info(self):

        dags = [self.airflow_dag_bag.get_dag(dag_id) for dag_id in self.airflow_dag_bag.dag_ids
                if not dag_id.startswith('airflow_')]  # Filter meta-DAGs

        data = []

        for d in dags:
            last_run = dag.get_last_dagrun(d.dag_id,
                                           self.airflow_session,
                                           include_externally_triggered=True)

            if last_run:
                run_state = last_run.get_state()
                run_date_info = self._get_localized_time(last_run.execution_date)

                last_successful_info = self._get_last_succesful_run_date(d)

                next_scheduled = d.following_schedule(datetime.now(pytz.utc))

                if next_scheduled:
                    next_scheduled_info = self._get_localized_time(next_scheduled)
                else:
                    next_scheduled_info = None

            else:
                run_state = None

                run_date_info = {}
                last_successful_info = {}
                next_scheduled_info = {}

            dag_info = {
                'name': d.dag_id,
                'description': d.description,
                'run_state': run_state,
                'run_date': run_date_info,
                'last_successful_date': last_successful_info,
                'next_scheduled_date': next_scheduled_info,
            }

            data.append(dag_info)

        return data

    def get_last_successful_dagrun(self, dags):
        successful_runs = [dag for dag in dags if dag['last_successful_date'].get('pst_time')]

        if successful_runs:
            return max(successful_runs, key=lambda x: x['last_successful_date']['pst_time'])

    def get_next_dagrun(self, dags):
        scheduled_runs = [dag for dag in dags if dag['next_scheduled_date'].get('pst_time')]

        if scheduled_runs:
            return min(scheduled_runs, key=lambda x: x['next_scheduled_date']['pst_time'])

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

    def _get_localized_time(self, date):
        pst_time = date.astimezone(PACIFIC_TIMEZONE)
        cst_time = date.astimezone(CENTRAL_TIMEZONE)

        return {
            'pst_time': pst_time,
            'cst_time': cst_time,
        }

    def _get_last_succesful_run_date(self, dag):
        run = self.airflow_session.query(dagrun.DagRun)\
                                  .filter(dagrun.DagRun.dag_id == dag.dag_id)\
                                  .filter(dagrun.DagRun.state == 'success')\
                                  .order_by(dagrun.DagRun.execution_date.desc())\
                                  .first()

        if run:
            return self._get_localized_time(run.execution_date)
        else:
            return {}


dashboard_package = {
    'name': 'Dashboard View',
    'category': 'Dashboard Plugin',
    'view': Dashboard()
}


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    appbuilder_views = [dashboard_package]
