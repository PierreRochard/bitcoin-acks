from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func

from bitcoin_acks.models import PullRequests
from bitcoin_acks.webapp.formatters import (
    author_link_formatter,
    body_formatter,
    humanize_date_formatter,
    labels_formatter,
    last_commit_state_formatter,
    line_count_formatter,
    mergeable_formatter,
    pr_link_formatter,
    review_decisions_formatter)


class PullRequestsModelView(ModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(PullRequestsModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'
        self.name = 'Pull Requests'

    def get_query(self):
        return self.session.query(self.model).order_by(self.model.is_high_priority.asc().nullslast())

    def get_count_query(self):
        return self.session.query(func.count(self.model.id))

    list_template = 'pull_requests_list.html'
    can_delete = False
    can_create = False
    can_edit = False
    can_view_details = True

    named_filter_urls = True

    details_modal = True

    column_searchable_list = [
        PullRequests.number,
        'title',
        'body',
        'author.login',
        'review_decisions.author.login',
        'labels.name'
    ]

    column_list = [
        'number',
        'author.login',
        'labels',
        'title',
        'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
    column_details_list = column_list
    column_filters = [
        'number',
        'author.login',
        'review_decisions.author.login',
        'labels.name',
        'title',
        'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
    column_sortable_list = [
        'number',
        'author.login',
        'title',
        'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
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
        'review_decisions_count': review_decisions_formatter,
        'mergeable': mergeable_formatter,
        'last_commit_state': last_commit_state_formatter,
        'labels': labels_formatter
    }
    column_default_sort = ('updated_at', True)
    column_labels = {
        'author.login': 'Author',
        'review_decisions.author.login': 'Reviewer',
        'labels.name': 'Label',
        'additions': '+',
        'deletions': '-',
        'created_at': 'Created',
        'updated_at': 'Updated',
        'merged_at': 'Merged',
        'closed_at': 'Closed',
        'review_decisions_count': 'Reviews',
        'last_commit_state': 'CI'
    }
