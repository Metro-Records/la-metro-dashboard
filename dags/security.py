from flask import flash, redirect, g, request, url_for
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.forms import LoginForm_db
from flask_appbuilder.security.views import AuthDBView, expose
from flask_login import login_user

from airflow.www_rbac.security import AirflowSecurityManager

class CustomAuthDBView(AuthDBView):
    """Redirect non-admins to Dashboard after login"""
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('Dashboard.list'))
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_db(
                form.username.data, form.password.data
            )
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)

            if 'Admin' in map(str, user.roles):
                next_url = request.args.get('next', '')
                return redirect(next_url)
            else:
                return redirect(url_for('Dashboard.list'))

        return self.render_template(
            self.login_template, title=self.title, form=form, appbuilder=self.appbuilder
        )

class CustomManager(AirflowSecurityManager):
    authdbview = CustomAuthDBView
