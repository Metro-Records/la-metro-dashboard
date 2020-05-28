import os

from airflow import settings
from airflow.models import dag, dagrun, taskinstance, xcom
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin

from datetime import datetime, timedelta
from dateutil import tz

import django

from flask import Blueprint
from flask_admin import BaseView, expose


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
            successful_run = dagrun.DagRun.find(dag_id=dag.dag_id, state='success', session=session, external_trigger=True)
            if successful_run:
                successful_event_runs.append(successful_runs[0])

        successful_bill_runs = []
        for dag in bill_dags:
            successful_runs = dagrun.DagRun.find(dag_id=dag.dag_id, state='success', session=session, external_trigger=True)
            if successful_runs:
                successful_bill_runs.append(successful_runs[0])

        successful_event_runs.sort(key=lambda x: x.end_date, reverse=True)
        successful_bill_runs.sort(key=lambda x: x.end_date, reverse=True)

        pst_tz = tz.gettz('America/Los_Angeles')
        cst_tz = tz.gettz('America/Chicago')

        if successful_event_runs != []:
            event_last_run = successful_event_runs[0]
            run_date = event_last_run.execution_date

            pst_run_time = run_date.astimezone(pst_tz)
            cst_run_time = run_date.astimezone(cst_tz)

            event_last_run_time = {
                'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
            }
        else:
            event_last_run = None
            event_last_run_time = None

        if successful_bill_runs != []:
            bill_last_run = successful_bill_runs[0]
            run_date = bill_last_run.execution_date

            pst_run_time = run_date.astimezone(pst_tz)
            cst_run_time = run_date.astimezone(cst_tz)

            bill_last_run_time = {
                'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
            }
        else:
            bill_last_run = None
            bill_last_run_time = None

        event_next_runs = [dag for dag in dag_info if dag['name'] in event_dags]
        event_next_runs.sort(key=lambda x: x.next_scheduled)
        if event_next_runs != []:
            event_next_run = event_next_runs[0]
            run_date = event_next_run.execution_date

            pst_run_time = run_date.astimezone(pst_tz)
            cst_run_time = run_date.astimezone(cst_tz)

            event_next_run_time = {
                'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
            }
        else:
            event_next_run = None
            event_next_run_time = None

        bill_next_runs = [dag for dag in dag_info if dag['name'] in bill_dags]
        bill_next_runs.sort(key=lambda x: x.next_scheduled)
        if bill_next_runs != []:
            bill_next_run = bill_next_runs[0]
            run_date = bill_next_run.execution_date

            pst_run_time = run_date.astimezone(pst_tz)
            cst_run_time = run_date.astimezone(cst_tz)

            bill_next_run_time = {
                'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
            }
        else:
            bill_next_run = None
            bill_next_run_time = None

        django_db_models = self.get_db_info()

        aware_now = datetime.now().replace(tzinfo=pst_tz)
        bills_in_index = xcom.XCom.get_one(execution_date=aware_now,\
                                           task_id='searchqueryset_count',\
                                           dag_id='searchqueryset_count',\
                                           include_prior_dates=True)

        metadata = {
            'data': dag_info,
            'event_last_run': event_last_run,
            'event_last_run_time': event_last_run_time,
            'event_next_run': event_next_run,
            'event_next_run_time': event_next_run_time,
            'events_in_db': django_db_models,
            'bill_last_run': bill_last_run,
            'bill_last_run_time': bill_last_run_time,
            'bill_next_run': bill_next_run,
            'bill_next_run_time': bill_next_run_time,
            # 'bills_in_db': ,
            'bills_in_index': bills_in_index
            # 'people_in_db':
        }

        return self.render('dashboard.html', data=metadata)

    def get_dag_info(self, dags, session):
        data = []
        for d in dags:
            if d.dag_id in ['councilmatic_showmigrations', 'hello_world', 'sample_windowed_bill_scraping', 'searchqueryset_count', 'sleep']:
                continue

            last_run = dag.get_last_dagrun(d.dag_id, session,include_externally_triggered=True) 

            if last_run:
                run_state = last_run.get_state()

                pst_tz = tz.gettz('America/Los_Angeles')
                cst_tz = tz.gettz('America/Chicago')
                
                run_date = last_run.execution_date

                pst_run_time = run_date.astimezone(pst_tz)
                cst_run_time = run_date.astimezone(cst_tz)
                run_date_info = {
                    'pst_time': datetime.strftime(pst_run_time, "%m/%d/%y %I:%M %p"),
                    'cst_time': datetime.strftime(cst_run_time, "%m/%d/%y %I:%M %p")
                }
                
                ti_states = [ti for ti in last_run.get_task_instances()]

                now = datetime.now()
                next_week = now + timedelta(days=7)
                next_scheduled = d.get_run_dates(now, next_week)[0]

                pst_next_scheduled = next_scheduled.astimezone(pst_tz)
                cst_next_scheduled = next_scheduled.astimezone(cst_tz)                
                next_scheduled_info = {
                    'pst_time': datetime.strftime(pst_next_scheduled, "%m/%d/%y %I:%M %p"),
                    'cst_time': datetime.strftime(cst_next_scheduled, "%m/%d/%y %I:%M %p")
                }

            else:
                run_state = 'Has Not Run'
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
        django.conf.settings.configure()
        django.setup()

        # LAMetroEventManager = django.db.models.LAMetroEventManager
        # return len(LAMetroEventManager.objects.get_queryset())
        return django.db.models


admin_view_ = Dashboard(category='Dashboard Plugin', name='Dashboard View')

blue_print_ = Blueprint('dashboard_plugin',
                        __name__,
                        template_folder='/app/templates',
                        static_folder='static',
                        static_url_path='/static/dashboard_plugin')


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    admin_views = [admin_view_]
    flask_blueprints = [blue_print_]
