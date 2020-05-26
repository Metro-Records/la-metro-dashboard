from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin

from datetime import datetime, timedelta
from dateutil import tz

from flask import Blueprint
from flask_admin import BaseView, expose


class Dashboard(BaseView):
    @expose('/')
    def index(self):
        bag = DagBag()
        all_dag_ids = bag.dag_ids
        all_dags = [bag.get_dag(dag_id) for dag_id in all_dag_ids]

        metadata = {
            'all_dags': all_dags,
            'data': []
        }


        for d in all_dags:
            if d.dag_id in ['councilmatic_showmigrations', 'hello_world', 'sample_windowed_bill_scraping', 'searchqueryset_count']:
                continue

            session = settings.Session()
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
            metadata['data'].append(dag_info)

        return self.render('dashboard.html', data=metadata)


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
