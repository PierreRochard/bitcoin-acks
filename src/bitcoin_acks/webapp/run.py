import os

from flask import Flask, flash, redirect, request, Response, url_for, session
from flask_admin import Admin
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_login import current_user, login_required, logout_user
from flask_security import SQLAlchemyUserDatastore, Security, login_user
from flask_admin.menu import MenuLink
from flask_dance.contrib.github import make_github_blueprint
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Invoices, PullRequests, Logs
from bitcoin_acks.models.bounties import Bounties
from bitcoin_acks.models.users import OAuth, Roles, Users
from bitcoin_acks.payments.payment_processor import PaymentProcessor
from bitcoin_acks.webapp.database import db
from bitcoin_acks.webapp.templates.template_globals import \
    apply_template_globals
from bitcoin_acks.webapp.views.bounties_payable_model_view import BountiesPayableModelView
from bitcoin_acks.webapp.views.invoices_model_view import InvoicesModelView
from bitcoin_acks.webapp.views.pull_requests_model_view import \
    PullRequestsModelView
from bitcoin_acks.webapp.views.user_model_view import UsersModelView


def create_app(config_object: str):
    app = Flask(__name__)

    app.config.from_object(config_object)

    db.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
    security = Security(datastore=user_datastore)
    security.init_app(app, user_datastore)

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
    admin.add_view(BountiesPayableModelView(Bounties, db.session))
    admin.add_view(InvoicesModelView(Invoices, db.session))
    admin.add_view(UsersModelView(Users, db.session))

    @app.route('/robots.txt')
    def robots_txt():
        return Response('User-agent: *\nDisallow: /\n')

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have logged out")
        return redirect(url_for("index"))

    app.payment_processor = PaymentProcessor()

    @app.route('/payment-notification/', methods=['POST'])
    def payment_notification():
        r = request.get_json()
        log.debug('invoice_notification', request=r, session=session)
        if 'data' in r:
            r = r['data']
        app.payment_processor.process_invoice_data(r)
        return {}

    github_blueprint = make_github_blueprint(
        client_id=os.environ['GITHUB_OAUTH_CLIENT_ID'],
        client_secret=os.environ['GITHUB_OAUTH_CLIENT_SECRET'],
        scope='user:email'
    )
    app.register_blueprint(github_blueprint, url_prefix='/login-github')

    twitter_blueprint = make_twitter_blueprint(
        api_key=os.environ['TWITTER_OAUTH_CLIENT_KEY'],
        api_secret=os.environ['TWITTER_OAUTH_CLIENT_SECRET'],
    )
    app.register_blueprint(twitter_blueprint, url_prefix='/login-twitter')

    @app.route("/login-twitter")
    def twitter_logged_in():
        if not twitter.authorized:
            return redirect(url_for("twitter.login"))
        user_resp = twitter.get("account/settings.json")
        log.debug('user response', resp=user_resp.json())
        assert user_resp.ok
        return "You are @{screen_name} on Twitter".format(screen_name=user_resp.json()["screen_name"])

    @oauth_authorized.connect_via(github_blueprint)
    def github_logged_in(github_blueprint, token):
        if not token:
            flash("Failed to log in.", category="error")
            return redirect(url_for("github.login"))

        user_resp = github_blueprint.session.get("/user")
        log.debug('user response', resp=user_resp.json())
        emails_resp = github_blueprint.session.get("/user/emails")
        log.debug('user emails response', resp=emails_resp.json())
        if not emails_resp.ok:
            log.error('github_logged_in error', resp=emails_resp.json(),
                      token=token)
            msg = "Failed to fetch user info."
            flash(msg, category="error")
            return False

        info = user_resp.json()
        user_id = info["node_id"]
        email = [e for e in emails_resp.json() if e['primary']][0]['email']

        with session_scope() as db_session:
            try:
                user = db_session.query(Users).filter(Users.id == user_id).one()
            except NoResultFound:
                user = Users(id=user_id)
                db_session.add(user)
            user.is_active = True
            user.email = email
            try:
                db_session.query(OAuth).filter_by(provider=github_blueprint.name, provider_user_id=user_id).one()
            except NoResultFound:
                oauth = OAuth(provider=github_blueprint.name, provider_user_id=user_id, user_id=user_id, token=token)
                db_session.add(oauth)
            login_user(user)
            flash("Successfully signed in.")
        return False

    # notify on OAuth provider error
    @oauth_error.connect_via(github_blueprint)
    def github_error(github_blueprint, message, response, error):
        msg = "OAuth error from {name}! message={message} response={response}".format(
            name=github_blueprint.name, message=message, response=response
        )
        flash(msg, category="error")

    class LoginMenuLink(MenuLink):

        def is_accessible(self):
            return not current_user.is_authenticated

    class LogoutMenuLink(MenuLink):

        def is_accessible(self):
            return current_user.is_authenticated

    admin.add_link(LoginMenuLink(name='Login', endpoint='github.login'))
    admin.add_link(LogoutMenuLink(name='Logout', endpoint='logout'))

    return app


if __name__ == '__main__':
    app = create_app('bitcoin_acks.webapp.settings.Config')
    app.debug = True
    app.run(host='0.0.0.0', port=7371)
