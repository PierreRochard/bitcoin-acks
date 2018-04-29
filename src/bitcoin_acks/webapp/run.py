from flask import Flask
from flask_admin import Admin

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.models import PullRequests
from bitcoin_acks.webapp.views import PullRequestsModelView


def create_app(config_object: str):
    app = Flask(__name__)

    app.config.from_object(config_object)

    with session_scope() as session:
        admin = Admin(app,
                      name='Bitcoin ACKs',
                      template_mode='bootstrap3',
                      url='/',
                      index_view=PullRequestsModelView(PullRequests, session))
    return app


if __name__ == '__main__':
    app = create_app('bitcoin_acks.webapp.settings.Config')
    app.debug = True
    app.run(port=7378)
