from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func

from bitcoin_acks.models import PullRequests
from bitcoin_acks.webapp.formatters import (
    author_link_formatter,
    body_formatter,
    concept_ack_formatter,
    humanize_date_formatter,
    labels_formatter,
    last_commit_state_formatter,
    line_count_formatter,
    mergeable_formatter,
    pr_link_formatter,
    tested_ack_formatter,
    untested_ack_formatter, nack_formatter)


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
        'review_decisions_count',
        'tested_acks_count',
        'untested_acks_count',
        'concept_acks_count',
        'nacks_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'updated_at',
        'merged_at',
        'closed_at'
    ]
    column_details_list = column_list
    column_filters = column_list + ['review_decisions.author.login']
    column_sortable_list = [
        'number',
        'author.login',
        'title',
        'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'concept_acks_count',
        'tested_acks_count',
        'untested_acks_count',
        'nacks_count',
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
        'concept_acks_count': concept_ack_formatter,
        'tested_acks_count': tested_ack_formatter,
        'untested_acks_count': untested_ack_formatter,
        'nacks_count': nack_formatter,
        'mergeable': mergeable_formatter,
        'last_commit_state': last_commit_state_formatter,
        'labels': labels_formatter
    }
    column_default_sort = ('updated_at', True)
    column_labels = {
        'author.login': 'Author',
        'additions': '+',
        'deletions': '-',
        'created_at': 'Created',
        'updated_at': 'Updated',
        'merged_at': 'Merged',
        'closed_at': 'Closed',
        'review_decisions_count': 'Reviews',
        'concept_acks_count': 'Concept ACKs',
        'tested_acks_count': 'Tested ACKs',
        'untested_acks_count': 'Untested ACKs',
        'nacks_count': 'NACKs',
        'last_commit_state': 'CI'
    }
