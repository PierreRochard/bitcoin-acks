from flask import Flask, request
from flask_admin import Admin

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.models import PullRequests, Logs
from bitcoin_acks.webapp.views import PullRequestsModelView


def create_app(config_object: str):
    app = Flask(__name__)

    app.config.from_object(config_object)

    @app.after_request
    def after_request(response):
        """ Logging after every request. """

        record = Logs()
        if request.headers.getlist("X-Forwarded-For"):
            record.ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            record.ip = request.remote_addr
        record.method = request.method
        record.full_path = request.full_path
        record.path = request.path
        record.user_agent = request.user_agent.string
        record.status = response.status_code

        with session_scope() as log_session:
            log_session.add(record)
        return response

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
    app.run(host='0.0.0.0', port=7371)
