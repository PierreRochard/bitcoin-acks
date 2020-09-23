from operator import or_

from flask_login import current_user
from sqlalchemy import func

from bitcoin_acks.webapp.formatters import humanize_date_formatter, \
    pr_link_formatter, satoshi_formatter
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class BountiesReceivableModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(BountiesReceivableModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'bounties-receivable'
        self.name = 'Bounties Receivable'

    form_columns = ['amount', 'pull_request']

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .filter(self.model.recipient_user_id == current_user.id)
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(self.model.recipient_user_id == current_user.id)
        )

    can_create = False

    named_filter_urls = True

    column_list = [
        'pull_request.number',
        'amount',
        'published_at'
    ]
    column_labels = {
        'pull_request.number': 'Pull Request',
        'amount': 'satoshis'
    }
    column_formatters = {
        'pull_request.number': pr_link_formatter,
        'published_at': humanize_date_formatter,
        'amount': satoshi_formatter
    }

    form_ajax_refs = {
        'pull_request': {
            'fields': ['number', 'title'],
            'page_size': 10,
            'minimum_input_length': 0,  # show suggestions, even before any user input
            'placeholder': 'Please select',
        }
    }