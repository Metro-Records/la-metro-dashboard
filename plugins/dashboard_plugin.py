from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin

from datetime import datetime, timedelta

from flask import Blueprint
from flask_admin import BaseView, expose


class DashboardView(BaseView):
    @expose('/')
    def index(self):
        bag = DagBag()
        all_dag_ids = bag.dag_ids
        all_dags = [bag.get_dag(dag_id) for dag_id in all_dag_ids]

        data = []

        for d in all_dags:
            session = settings.Session()
            last_run = dag.get_last_dagrun(d.dag_id, session,include_externally_triggered=True) 

            if last_run:
                run_state = last_run.get_state()
                
                run_date = last_run.execution_date
                run_date_info = {
                    'date': run_date.date(),
                    'hour': run_date.hour,
                    'minute': run_date.minute
                }
                
                ti_states = [ti for ti in last_run.get_task_instances()]

                now = datetime.now()
                next_week = now + timedelta(days=7)
                next_scheduled = d.get_run_dates(now, next_week)[0]
                next_scheduled_info = {
                    'date': next_scheduled.date(),
                    'hour': next_scheduled.hour,
                    'minute': next_scheduled.minute
                }

            else:
                run_state = 'Has Not Run'
                run_date_info = None
                ti_states = []
                next_scheduled_info = None

            dag_info = {
                'name': d.dag_id,
                'run_state': run_state,
                'run_date': run_date_info,
                'scrapes_completed': ti_states,
                'next_scheduled': next_scheduled_info
            }
            data.append(dag_info)

        return self.render('dashboard.html', data=data)


admin_view_ = DashboardView(category='Dashboard Plugin', name='Dashboard View')

blue_print_ = Blueprint('dashboard_plugin',
                        __name__,
                        template_folder='/app/templates',
                        static_folder='static',
                        static_url_path='/static/dashboard_plugin')


class AirflowDashboardPlugin(AirflowPlugin):
    name = 'dashboard_plugin'
    admin_views = [admin_view_]
    flask_blueprints = [blue_print_]
