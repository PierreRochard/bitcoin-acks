from flask import abort, redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user


class AuthenticatedModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('github.login', next=request.url))

    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = False
    column_display_actions = False
