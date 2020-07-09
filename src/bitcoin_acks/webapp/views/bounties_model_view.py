from datetime import datetime
from uuid import uuid4

from flask import abort, redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user

from bitcoin_acks.models import Bounties
from bitcoin_acks.webapp.formatters import humanize_date_formatter, \
    pr_link_formatter


class BountiesModelView(ModelView):
    form_base_class = SecureForm

    def __init__(self, model, session, *args, **kwargs):
        super(BountiesModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'bounties'
        self.name = 'Bounties'

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

    form_columns = ['amount', 'pull_request']

    def on_model_change(self, form, model: Bounties, is_created):
        model.id = uuid4().hex
        model.published_at = datetime.utcnow()
        model.creator_id = current_user.id

    can_create = True
    can_delete = False
    can_edit = False
    can_view_details = False
    column_display_actions = False

    named_filter_urls = True

    details_modal = True

    column_list = [
        'pull_request.number',
        'amount',
        'published_at'
    ]

    column_formatters = {
        'pull_request.number': pr_link_formatter,
        'published_at': humanize_date_formatter,
    }

    form_ajax_refs = {
        'pull_request': {
            'fields': ['number', 'title'],
            'page_size': 10,
            'minimum_input_length': 0,  # show suggestions, even before any user input
            'placeholder': 'Please select',
        }
    }