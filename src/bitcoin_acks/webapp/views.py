from flask_admin.contrib.sqla import ModelView

from bitcoin_acks.models import PullRequests
from bitcoin_acks.webapp.formatters import (
    body_formatter,
    pr_link_formatter,
    author_link_formatter,
    humanize_date_formatter, line_count_formatter, ack_comment_count_formatter,
    mergeable_formatter, last_commit_state_formatter, labels_formatter)


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

    details_modal = True

    column_searchable_list = [
        PullRequests.number,
        'title',
        'body',
        'author.login'
    ]

    column_list = [
        'number',
        'author.login',
        'labels',
        'title',
        'body',
        'additions',
        'deletions',
        'ack_comment_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
    column_details_list = column_list
    column_filters = column_list
    column_sortable_list = [c for c in column_list if c != 'labels']
    column_formatters = {
        'body': body_formatter,
        'number': pr_link_formatter,
        'author.login': author_link_formatter,
        'created_at': humanize_date_formatter,
        'updated_at': humanize_date_formatter,
        'merged_at': humanize_date_formatter,
        'closed_at': humanize_date_formatter,
        'additions': line_count_formatter,
        'deletions': line_count_formatter,
        'ack_comment_count': ack_comment_count_formatter,
        'mergeable': mergeable_formatter,
        'last_commit_state': last_commit_state_formatter,
        'labels': labels_formatter
    }
    column_default_sort = ('number', True)
    column_labels = {
        'author.login': 'Author',
        'additions': '+',
        'deletions': '-',
        'created_at': 'Created',
        'updated_at': 'Updated',
        'merged_at': 'Merged',
        'closed_at': 'Closed',
        'ack_comment_count': 'ACKs',
        'last_commit_state': 'CI'
    }
