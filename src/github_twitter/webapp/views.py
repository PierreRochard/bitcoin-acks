from flask_admin.contrib.sqla import ModelView

from github_twitter.models import Users, PullRequests
from github_twitter.webapp.formatters import body_formatter, user_formatter


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
    # inline_models = (Users, )
    column_searchable_list = [
        PullRequests.number,
        'title',
        'body',
        'user.login'
    ]

    column_list = [
        'number',
        'user.login',
        'state',
        'title',
        'body',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at',
        'locked'
    ]
    column_filters = column_list
    column_formatters = dict(
        body=body_formatter,
        user=user_formatter
    )
    column_default_sort = ('number', True)
