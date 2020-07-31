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
    AIRFLOW_DAG_BAG = DagBag()

    BILL_DAGS = (
        'windowed_bill_scraping',
        'daily_scraping',
        'friday_hourly_scraping',
        'saturday_hourly_scraping',
    )

    EVENT_DAGS = (
        'windowed_event_scraping',
        'daily_scraping',
        'friday_hourly_scraping',
        'saturday_hourly_scraping',
    )

    DATETIME_FORMAT = '%m/%d/%y %I:%M %p'

    @expose('/')
    def list(self):
        dag_info = self.get_dag_info()

        event_dags = [dag for dag in dag_info if dag['name'] in self.EVENT_DAGS]
        bill_dags = [dag for dag in dag_info if dag['name'] in self.BILL_DAGS]

        event_last_run, event_last_run_time = self.get_last_successful_dagrun(event_dags)
        bill_last_run, bill_last_run_time = self.get_last_successful_dagrun(bill_dags)

        event_next_run = self.get_next_dagrun(event_dags)
        bill_next_run = self.get_next_dagrun(bill_dags)

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

    def get_dag_info(self):

        dags = [self.AIRFLOW_DAG_BAG.get_dag(dag_id) for dag_id in self.AIRFLOW_DAG_BAG.dag_ids
                if not dag_id.startswith('airflow_')]  # Filter meta-DAGs

        data = []

        for d in dags:
            last_run = dag.get_last_dagrun(d.dag_id,
                                           self.AIRFLOW_SESSION,
                                           include_externally_triggered=True)

            if last_run:
                run_state = last_run.get_state()
                run_date_info = self._get_localized_time(last_run.execution_date)

                last_successful, last_successful_info = self._get_last_successful_dagrun(d)

                next_scheduled = d.following_schedule(datetime.now(pytz.utc))
                next_scheduled_info = self._get_localized_time(next_scheduled)

            else:
                run_state = None
                run_date_info = self._get_localized_time(None)

                last_successful = None
                last_successful_info = self._get_localized_time(None)

                next_scheduled_info = self._get_localized_time(None)

            dag_info = {
                'name': d.dag_id,
                'description': d.description,
                'run_state': run_state,
                'run_date': run_date_info,
                'last_successful': last_successful,
                'last_successful_date': last_successful_info,
                'next_scheduled': next_scheduled_info
            }

            data.append(dag_info)

        return data

    def get_last_successful_dagrun(self, dags):
        last = max(
            dag for dag in dags if dag['last_successful_date']['pst_time'],
            key=lambda x: x['last_successful_date']['pst_time']
        )
        return last['last_successful'], last['last_successful_date']

    def get_next_dagrun(self, dags):
        return min(
            dag for dag in dags if dag['last_successful_date']['pst_time'],
            key=lambda x: x['next_scheduled']['pst_time']
        )

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
        if date:
            pst_time = datetime.strftime(date.astimezone(PACIFIC_TIMEZONE), self.DATETIME_FORMAT)
            cst_time = datetime.strftime(date.astimezone(CENTRAL_TIMEZONE), self.DATETIME_FORMAT)

        else:
            pst_time, cst_time = None, None

        return {
            'pst_time': pst_time,
            'cst_time': cst_time,
        }

    def _get_last_successful_dagrun(self, dag):
        run = self.AIRFLOW_SESSION.query(dagrun.DagRun)\
                                  .filter(dagrun.DagRun.dag_id == dag.dag_id)\
                                  .filter(dagrun.DagRun.state == 'success')\
                                  .order_by(dagrun.DagRun.execution_date.desc())\
                                  .first()

        if run:
            run_time = self._get_localized_time(run.execution_date)
        else:
            run_time = self._get_localized_time(None)

        return (run, run_time)


dashboard_package = {
    'name': 'Dashboard View',
    'category': 'Dashboard Plugin',
    'view': Dashboard()
}


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    appbuilder_views = [dashboard_package]
