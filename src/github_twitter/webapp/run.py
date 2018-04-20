from flask import Flask
from flask_admin import Admin

from github_twitter.database.session import session_scope
from github_twitter.models import PullRequests
from github_twitter.webapp.views import PullRequestsModelView

app = Flask(__name__)
app.debug = True
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.secret_key = 'aS2MPk5uGu8PnTFLAK'

with session_scope() as session:
    admin = Admin(app,
                  name='Bitcoin ACKs',
                  template_mode='bootstrap3',
                  url='/',
                  index_view=PullRequestsModelView(PullRequests, session))

app.run(port=5023)
