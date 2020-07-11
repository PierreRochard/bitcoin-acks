from datetime import datetime
from operator import or_
from uuid import uuid4

from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce

from bitcoin_acks.database import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Bounties
from bitcoin_acks.webapp.formatters import humanize_date_formatter, \
    pr_link_formatter, satoshi_formatter
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class BountiesModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(BountiesModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'bounties'
        self.name = 'Bounties'

    form_columns = ['amount', 'pull_request']

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .filter(or_(self.model.payer_user_id == current_user.id,
                            self.model.recipient_user_id == current_user.id))
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(or_(self.model.payer_user_id == current_user.id,
                            self.model.recipient_user_id == current_user.id))
        )

    def on_model_change(self, form, model: Bounties, is_created: bool):
        model.id = uuid4().hex
        model.published_at = datetime.utcnow()
        model.payer_user_id = current_user.id
        model.recipient_user_id = model.pull_request.author_id

        with session_scope() as session:
            total_bounty_amount = (
                session
                    .query(coalesce(func.sum(Bounties.amount), 0))
                    .filter(Bounties.pull_request_id == model.pull_request.id)
                    .one()
            )[0]
            log.debug('total_satoshis', total_bounty_amount=total_bounty_amount)
            model.pull_request.total_bounty_amount = total_bounty_amount + model.amount

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