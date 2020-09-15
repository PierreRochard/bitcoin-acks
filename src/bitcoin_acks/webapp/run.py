import os

from flask import Flask, flash, redirect, request, Response, url_for
from flask_admin import Admin
from flask_dance.consumer import oauth_authorized, oauth_error
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
from bitcoin_acks.webapp.database import db
from bitcoin_acks.webapp.templates.template_globals import \
    apply_template_globals
from bitcoin_acks.webapp.views.bounties_model_view import BountiesModelView
from bitcoin_acks.webapp.views.payables_model_view import PayablesModelView
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
    admin.add_view(BountiesModelView(Bounties, db.session))
    admin.add_view(PayablesModelView(Invoices, db.session))
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

    blueprint = make_github_blueprint(
        client_id=os.environ['GITHUB_OAUTH_CLIENT_ID'],
        client_secret=os.environ['GITHUB_OAUTH_CLIENT_SECRET'],
        scope='user:email'
    )
    app.register_blueprint(blueprint, url_prefix='/login')

    # create/login local user on successful OAuth login
    @oauth_authorized.connect_via(blueprint)
    def github_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in.", category="error")
            return False

        user_resp = blueprint.session.get("/user")
        log.debug('user response', resp=user_resp.json())
        emails_resp = blueprint.session.get("/user/emails")
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

        # Find this OAuth token in the database, or create it
        with session_scope() as session:
            query = (
                session
                    .query(OAuth)
                    .filter_by(provider=blueprint.name,
                               provider_user_id=user_id)
            )
            try:
                oauth = query.one()
            except NoResultFound:
                oauth = OAuth(provider=blueprint.name,
                              provider_user_id=user_id,
                              token=token)
                session.add(oauth)

            if oauth.user:
                oauth.user.email = email
                login_user(oauth.user)
                flash("Successfully signed in.")
            else:
                # Create a new local user account for this user
                user = Users(id=user_id, email=email, is_active=True)
                # Associate the new local user account with the OAuth token
                oauth.user = user
                # Save and commit our database models
                session.add_all([user, oauth])
                session.commit()
                # Log in the new local user account
                login_user(user)
                flash("Successfully signed in.")

        # Disable Flask-Dance's default behavior for saving the OAuth token
        return False

    # notify on OAuth provider error
    @oauth_error.connect_via(blueprint)
    def github_error(blueprint, message, response, error):
        msg = "OAuth error from {name}! message={message} response={response}".format(
            name=blueprint.name, message=message, response=response
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
