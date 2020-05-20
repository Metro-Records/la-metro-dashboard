from airflow import settings
from airflow.models import dag, dagrun, taskinstance
from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin

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
            run_state = last_run.get_state() if last_run else 'Has Not Run'

            run_date = last_run.execution_date if last_run else None
            run_date_info = {'date': run_date.date(), 'hour': run_date.hour, 'minute': run_date.minute} if last_run else None
            
            ti_states = [ti for ti in last_run.get_task_instances()] if last_run else []

            dag_info = {
                'name': d.dag_id,
                'run_state': run_state,
                'run_date': run_date_info,
                'scrapes_completed': ti_states
                # 'next_scheduled':
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
