from flask import request
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func

from bitcoin_acks.logging import log
from bitcoin_acks.models import PullRequests
from bitcoin_acks.webapp.formatters import (
    author_link_formatter,
    body_formatter,
    bounty_formatter, humanize_date_formatter,
    labels_formatter,
    last_commit_state_formatter,
    line_count_formatter,
    mergeable_formatter,
    pr_link_formatter,
    review_decisions_formatter, satoshi_formatter)
from bitcoin_acks.webapp.mixins import NullOrderMixinView


class BitcoinPullRequestsModelView(ModelView, NullOrderMixinView):
    def __init__(self, model, session, *args, **kwargs):
        super(BitcoinPullRequestsModelView, self).__init__(model, session, *args,
                                                           **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'
        self.name = 'Bitcoin'

    def get_query(self):
        log.debug('get_query', request=request.args)
        if request.args.get('sort'):
            return super().get_query()
        query = (
            self.session.query(self.model)
                .order_by(self.model.is_high_priority.asc().nullslast())
                .filter(self.model.repository_id)
        )
        if self._get_list_extra_args().sort is None:
            query = query.order_by(self.model.last_commit_pushed_date.desc().nullslast())
        return query

    def get_count_query(self):
        return self.session.query(func.count(self.model.id))

    list_template = 'pull_requests_list.html'
    page_size = 50
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
        'total_bounty_amount',
        'labels',
        'title',
        # 'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'last_commit_pushed_date',
        # 'merged_at',
        'closed_at'
    ]
    column_details_list = column_list
    column_filters = [
        'number',
        'author.login',
        'total_bounty_amount',
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
        'last_commit_pushed_date',
        'merged_at',
        'closed_at'
    ]
    column_sortable_list = [
        'number',
        'author.login',
        'total_bounty_amount',
        'title',
        'body',
        'additions',
        'deletions',
        'review_decisions_count',
        'mergeable',
        'last_commit_state',
        'created_at',
        'last_commit_pushed_date',
        'merged_at',
        'closed_at'
    ]
    column_formatters = {
        'body': body_formatter,
        'number': pr_link_formatter,
        'author.login': author_link_formatter,
        'created_at': humanize_date_formatter,
        'last_commit_pushed_date': humanize_date_formatter,
        'merged_at': humanize_date_formatter,
        'closed_at': humanize_date_formatter,
        'additions': line_count_formatter,
        'deletions': line_count_formatter,
        'review_decisions_count': review_decisions_formatter,
        'mergeable': mergeable_formatter,
        'last_commit_state': last_commit_state_formatter,
        'labels': labels_formatter,
        'total_bounty_amount': bounty_formatter
    }
    # column_default_sort = ('last_commit_pushed_date', 'LAST')
    column_labels = {
        'author.login': 'Author',
        'review_decisions.author.login': 'Reviewer',
        'labels.name': 'Label',
        'total_bounty_amount': 'Bounty Pledged',
        'additions': '+',
        'deletions': '-',
        'created_at': 'Created',
        'last_commit_pushed_date': 'Last Commit Pushed',
        'merged_at': 'Merged',
        'closed_at': 'Closed',
        'review_decisions_count': 'Reviews',
        'last_commit_state': 'CI'
    }
