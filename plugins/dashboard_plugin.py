from airflow.models.dagbag import DagBag
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from flask_admin import BaseView, expose


class DashboardView(BaseView):
    @expose('/')
    def index(self):
        dagbag = DagBag()
        dag_ids = dagbag.dag_ids
        all_dags = [dagbag.get_dag(dag_id) for dag_id in dag_ids]
        return self.render('dashboard.html', data=all_dags)


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
