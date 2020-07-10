from datetime import datetime
from uuid import uuid4

from flask_login import current_user
from sqlalchemy import func, or_

from bitcoin_acks.database import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Bounties
from bitcoin_acks.models.invoices import Invoices
from bitcoin_acks.webapp.formatters import humanize_date_formatter, \
    pr_link_formatter, satoshi_formatter
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class InvoicesModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(InvoicesModelView, self).__init__(model, session, *args,
                                                **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'invoices'
        self.name = 'Invoices'

    form_columns = ['bounty']

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .filter(or_(self.model.recipient_user_id == current_user.id,
                            self.model.payer_user_id == current_user.id))
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(or_(self.model.recipient_user_id == current_user.id,
                            self.model.payer_user_id == current_user.id))
        )

    def on_model_change(self, form, model: Invoices, is_created: bool):
        if not is_created:
            raise Exception('Can not edit invoices.')
        model.data = model.recipient.btcpay_client.create_invoice(
            {"price": model.bounty.amount, "currency": "BTC"}
        )
        model.id = model.data['id']
        model.published_at = datetime.utcnow()
        model.payer_user_id = model.bounty.payer_user_id
        assert model.payer_user_id == current_user.id
        model.recipient_user_id = model.bounty.recipient_user_id


    can_create = True

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