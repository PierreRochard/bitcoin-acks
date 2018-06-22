from flask import Flask, request, Response
from flask_admin import Admin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from bitcoin_acks.database.session import session_scope, get_url
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

    pg_url = get_url()
    engine = create_engine(pg_url, connect_args={'sslmode': 'prefer'})
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    admin = Admin(app,
                  name='Bitcoin ACKs',
                  template_mode='bootstrap3',
                  url='/',
                  index_view=PullRequestsModelView(PullRequests, session))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        Session.remove()

    @app.route('/robots.txt')
    def robots_txt():
        return Response('User-agent: *\nDisallow: /\n')

    return app


if __name__ == '__main__':
    app = create_app('bitcoin_acks.webapp.settings.Config')
    app.debug = True
    app.run(host='0.0.0.0', port=7371)
