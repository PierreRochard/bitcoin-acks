from flask_admin.contrib.sqla import ModelView

from github_twitter.models import PullRequests
from github_twitter.webapp.formatters import (
    body_formatter,
    pr_link_formatter,
    user_link_formatter,
    humanize_date_formatter)


class PullRequestsModelView(ModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(PullRequestsModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'
        self.name = 'Pull Requests'

    can_delete = False
    can_create = False
    can_edit = False
    can_view_details = True

    column_searchable_list = [
        PullRequests.number,
        'title',
        'body',
        'user.login'
    ]

    column_list = [
        'number',
        'user.login',
        'diff.added_lines',
        'diff.removed_lines',
        'state',
        'title',
        'body',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
    column_filters = column_list
    column_sortable_list = column_list
    column_formatters = {
        'body': body_formatter,
        'number': pr_link_formatter,
        'title': pr_link_formatter,
        'user.login': user_link_formatter,
        'created_at': humanize_date_formatter,
        'updated_at': humanize_date_formatter,
        'merged_at': humanize_date_formatter,
        'closed_at': humanize_date_formatter

    }
    column_default_sort = ('number', True)