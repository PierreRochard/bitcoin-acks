from datetime import datetime

from bitcoin.core import COIN
from flask import flash, redirect, url_for, request, session
from flask_admin import expose
from flask_login import current_user
from requests import Response, RequestException
from sqlalchemy import func, or_

from bitcoin_acks.database import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Users, Bounties
from bitcoin_acks.models.invoices import Invoices
from bitcoin_acks.payments.recipient_btcpay import RecipientBTCPay
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

    @expose('/generate-invoice/<bounty_id>/<recipient_user_id>/')
    def generate_invoice(self, bounty_id: str, recipient_user_id: str):
        with session_scope() as db_session:
            bounty: Bounties = db_session.query(Bounties).filter(Bounties.id == bounty_id).one()
            recipient: Users = db_session.query(Users).filter(Users.id == recipient_user_id).one()
            if recipient.btcpay_client is None:
                flash(f'{recipient.best_name} does not have BTCPay configured here. Elsewhere they may have other ways '
                      f'of receiving payments (Patreon, static address, etc).')
                return redirect(url_for('bounties-payable.index_view'))
            try:
                recipient_btcpay = RecipientBTCPay(client=recipient.btcpay_client)
                invoice_data = recipient_btcpay.get_pull_request_invoice(
                    amount=bounty.amount,
                    bounty_id=bounty_id,
                    pull_request_number=bounty.pull_request.number
                )
                invoice_model = Invoices()
                invoice_model.bounty_id = bounty.id
                invoice_model.id = invoice_data['id']
                invoice_model.status = invoice_data['status']
                invoice_model.url = invoice_data['url']
                invoice_model.recipient_user_id = recipient_user_id
                invoice_model.payer_user_id = bounty.payer_user_id
                db_session.add(invoice_model)
                return redirect(invoice_model.url)
            except RequestException as e:
                log.debug('RequestException', exception=e, request=e.request, response=e.response)
                try:
                    r: Response = e.response
                    flash(f'{r.status_code} - {r.text}', category='error')
                except AttributeError as e:
                    flash('Request error')
                return redirect(url_for('users.index_view'))

    can_create = False

    column_list = [
        'id',
        'status',
        'url',
        'recipient_user_id'
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
