from datetime import datetime

from bitcoin.core import COIN
from flask import flash, redirect, url_for
from flask_login import current_user
from requests import Response, RequestException
from sqlalchemy import func, or_

from bitcoin_acks.database import session_scope
from bitcoin_acks.models import Users
from bitcoin_acks.models.invoices import Invoices
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
                .filter(self.model.payer_user_id == current_user.id)
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(self.model.payer_user_id == current_user.id)
        )

    def on_model_change(self, form, model: Invoices, is_created: bool):
        if not is_created:
            raise Exception('Can not edit invoices.')
        model.published_at = datetime.utcnow()
        model.payer_user_id = model.bounty.payer_user_id
        assert model.payer_user_id == current_user.id
        model.recipient_user_id = model.bounty.recipient_user_id
        with session_scope() as session:
            recipient = session.query(Users).filter(Users.id == model.recipient_user_id).one()
            if recipient.btcpay_client is None:
                return
            try:
                model.data = recipient.btcpay_client.create_invoice(
                    {
                        'price': model.bounty.amount/COIN,
                        'currency': 'BTC'
                    }
                )
                model.id = model.data['id']
                model.status = model.data['status']
                model.url = model.data['url']
            except RequestException as e:
                try:
                    r: Response = e.response
                    flash(f'{r.status_code} - {r.text}', category="error")
                except AttributeError:
                    flash('Request error')
                return redirect(url_for('users.index_view'))

    can_create = True

    column_list = [
        'id',
        'status',
        'url'
    ]
    column_labels = {
        # 'pull_request.number': 'Pull Request',
        # 'amount': 'satoshis'
    }
    column_formatters = {
        # 'pull_request.number': pr_link_formatter,
        # 'published_at': humanize_date_formatter,
        # 'amount': satoshi_formatter
    }

    form_ajax_refs = {
        'bounty': {
            'fields': ['id', 'amount'],
            'page_size': 10,
            'minimum_input_length': 0,
            # show suggestions, even before any user input
            'placeholder': 'Please select',
        }
    }
