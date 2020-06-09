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
from flask_admin import BaseView, expose

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from dags.base import DjangoOperator

PACIFIC_TIMEZONE = pytz.timezone('US/Pacific')
CENTRAL_TIMEZONE = pytz.timezone('US/Central')


class Dashboard(BaseView):
    @expose('/')
    def index(self):
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
                if 'event' in ti.task_id and current_dag not in event_dags:
                    event_dags.append(current_dag)
                elif 'bill' in ti.task_id and current_dag not in bill_dags:
                    bill_dags.append(current_dag)
                elif 'daily' in ti.task_id and current_dag not in bill_dags and current_dag not in event_dags:
                    event_dags.append(current_dag)
                    bill_dags.append(current_dag)

        successful_event_runs = []
        for dag in event_dags:
            successful_runs = dagrun.DagRun.find(dag_id=dag.dag_id, state='success', session=session, external_trigger=True)
            if successful_runs:
                successful_event_runs.append(successful_runs[0])
        successful_event_runs.sort(key=lambda x: x.end_date, reverse=True)
        event_last_run, event_last_run_time = self.get_run_info(successful_event_runs)

        successful_bill_runs = []
        for dag in bill_dags:
            successful_runs = dagrun.DagRun.find(dag_id=dag.dag_id, state='success', session=session, external_trigger=True)
            if successful_runs:
                successful_bill_runs.append(successful_runs[0])
        successful_bill_runs.sort(key=lambda x: x.end_date, reverse=True)
        bill_last_run, bill_last_run_time = self.get_run_info(successful_bill_runs)

        event_next_runs = [dag for dag in dag_info if dag['name'] in event_dags]
        event_next_runs.sort(key=lambda x: x.next_scheduled)
        event_next_run, event_next_run_time = self.get_run_info(event_next_runs)

        bill_next_runs = [dag for dag in dag_info if dag['name'] in bill_dags]
        bill_next_runs.sort(key=lambda x: x.next_scheduled)
        bill_next_run, bill_next_run_time = self.get_run_info(bill_next_runs)

        events_in_db, bills_in_db, bills_in_index = self.get_db_info()
        
        metadata = {
            'data': dag_info,
            'event_last_run': event_last_run,
            'event_last_run_time': event_last_run_time,
            'event_next_run': event_next_run,
            'event_next_run_time': event_next_run_time,
            'events_in_db': events_in_db,
            'bill_last_run': bill_last_run,
            'bill_last_run_time': bill_last_run_time,
            'bill_next_run': bill_next_run,
            'bill_next_run_time': bill_next_run_time,
            'bills_in_db': bills_in_db,
            'bills_in_index': bills_in_index,
        }

        return self.render('dashboard.html', data=metadata)

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
                
                ti_states = [ti for ti in last_run.get_task_instances()]

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
                ti_states = []
                next_scheduled_info = None

            dag_info = {
                'name': d.dag_id,
                'description': d.description,
                'run_state': run_state,
                'run_date': run_date_info,
                'scrapes_completed': ti_states,
                'next_scheduled': next_scheduled_info
            }

            data.append(dag_info)

        return data

    def get_db_info(self):
        DjangoOperator.setup_django()

        Events = django.apps.apps.get_model('lametro', 'LAMetroEvent')
        total_events = len(Events.objects.get_queryset())

        Bills = django.apps.apps.get_model('lametro', 'LAMetroBill')
        total_bills = len(Bills.objects.get_queryset())

        from haystack.query import SearchQuerySet
        bills_in_index = len(SearchQuerySet().all())

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


admin_view_ = Dashboard(category='Dashboard Plugin', name='Dashboard View')

blue_print_ = Blueprint('dashboard_plugin',
                        __name__,
                        template_folder=os.path.join(os.environ['AIRFLOW_HOME'], 'templates'),
                        static_folder='static',
                        static_url_path='/static/dashboard_plugin')


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    admin_views = [admin_view_]
    flask_blueprints = [blue_print_]
