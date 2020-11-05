from btcpay import BTCPayClient
from flask_login import current_user
from sqlalchemy import func

from bitcoin_acks.models import Users
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class UsersRepositoriesModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(UsersRepositoriesModelView, self).__init__(model, session, *args,
                                             **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'repositories'
        self.name = 'Repositories'

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .filter(self.model.user_id == current_user.id)
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(self.model.id == current_user.id)
        )

    def on_model_change(self, form, model: Users, is_created: bool):
        if is_created:
            raise Exception('Can not create users')

        if model.btcpay_host is None:
            model.btcpay_client = None

        if model.btcpay_pairing_code is not None:
            model.btcpay_client = BTCPayClient.create_client(
                host=model.btcpay_host,
                code=model.btcpay_pairing_code
            )
        model.btcpay_pairing_code = None

    can_edit = True
    column_display_actions = True
