import os
import sys

import pytz
from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin

from datetime import datetime

import django

from flask import Blueprint
from flask_appbuilder import BaseView, expose

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from dags.base import DjangoOperator

PACIFIC_TIMEZONE = pytz.timezone('US/Pacific')
CENTRAL_TIMEZONE = pytz.timezone('US/Central')


class Dashboard(BaseView):
    template_folder = os.path.join(os.path.dirname(__file__), 'templates')

    @expose('/')
    def list(self):
        session = settings.Session()
        bag = DagBag()
        all_dag_ids = bag.dag_ids
        all_dags = [bag.get_dag(dag_id) for dag_id in all_dag_ids]

        dag_info = self.get_dag_info(all_dags, session)

        latest_dagruns = dagrun.DagRun.get_latest_runs(session)
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

        successful_event_runs = []
        for event_dag in event_dags:
            last_successful_run = self.get_last_successful_run(event_dag.dag_id, session)
            if last_successful_run:
                successful_event_runs.append(last_successful_run)
        successful_event_runs.sort(key=lambda x: x.end_date, reverse=True)
        event_last_run, event_last_run_time = self.get_run_info(successful_event_runs)

        successful_bill_runs = []
        for bill_dag in bill_dags:
            last_successful_run = self.get_last_successful_run(bill_dag.dag_id, session)
            if last_successful_run:
                successful_bill_runs.append(last_successful_run)
        successful_bill_runs.sort(key=lambda x: x.end_date, reverse=True)
        bill_last_run, bill_last_run_time = self.get_run_info(successful_bill_runs)

        bill_dag_ids = [bill_dag.dag_id for bill_dag in bill_dags]
        event_dag_ids = [event_dag.dag_id for event_dag in event_dags]

        event_next_runs = [dag for dag in dag_info if dag['name'] in event_dag_ids]
        event_next_runs.sort(key=lambda x: x['next_scheduled']['pst_time'])
        if len(event_next_runs) > 0:
            event_next_run = event_next_runs[0]
        else:
            event_next_run = None

        bill_next_runs = [dag for dag in dag_info if dag['name'] in bill_dag_ids]
        bill_next_runs.sort(key=lambda x: x['next_scheduled']['pst_time'])
        if len(bill_next_runs) > 0:
            bill_next_run = bill_next_runs[0]
        else:
            bill_next_run = None

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

    def get_dag_info(self, dags, session):
        data = []
        for d in dags:
            last_run = dag.get_last_dagrun(d.dag_id, session,include_externally_triggered=True) 

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
        DjangoOperator.setup_django()

        Events = django.apps.apps.get_model('lametro', 'LAMetroEvent')
        total_events = Events.objects.count()

        Bills = django.apps.apps.get_model('lametro', 'LAMetroBill')
        total_bills = Bills.objects.count()

        from haystack.query import SearchQuerySet
        bills_in_index = SearchQuerySet().count()

        return (total_events, total_bills, bills_in_index)

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

    def get_last_successful_run(self, dag_id, session):
        """
        Given a DAG ID and a SQLAlchemy Session object, return the last successful
        DagRun.
        """
        return session.query(dagrun.DagRun)\
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
