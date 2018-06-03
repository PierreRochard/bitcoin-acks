import os

from flask import Flask, request, Response
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.menu import MenuLink
from flask_dance.contrib.github import make_github_blueprint, github

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.models import PullRequests, Logs
from bitcoin_acks.webapp.templates.template_globals import \
    apply_template_globals
from bitcoin_acks.webapp.views import PullRequestsModelView


def create_app(config_object: str):
    app = Flask(__name__)

    app.config.from_object(config_object)
    db = SQLAlchemy(app)
    apply_template_globals(app)

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

    admin = Admin(app,
                  name='Bitcoin ACKs',
                  template_mode='bootstrap3',
                  url='/',
                  index_view=PullRequestsModelView(PullRequests, db.session))


    @app.route('/robots.txt')
    def robots_txt():
        return Response('User-agent: *\nDisallow: /\n')

    blueprint = make_github_blueprint(
        client_id=os.environ['GITHUB_OAUTH_CLIENT_ID'],
        client_secret=os.environ['GITHUB_OAUTH_CLIENT_SECRET'],
        scope='user:email'
    )
    app.register_blueprint(blueprint, url_prefix='/login')

    admin.add_link(MenuLink(name='Login', endpoint='github.login'))

    return app


if __name__ == '__main__':
    app = create_app('bitcoin_acks.webapp.settings.Config')
    app.debug = True
    app.run(host='0.0.0.0', port=7371)
