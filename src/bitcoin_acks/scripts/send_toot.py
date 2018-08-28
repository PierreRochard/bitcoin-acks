import datetime
import os

import requests
from mastodon import Mastodon

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.models import PullRequests
from bitcoin_acks.models.toots import Toots

MASTODON_CREDPATH = os.environ['MASTODON_CREDPATH']
MASTODON_APPNAME = os.environ['MASTODON_APPNAME']
MASTODON_INSTANCE = os.environ['MASTODON_INSTANCE']
MASTODON_USER = os.environ['MASTODON_USER']
MASTODON_PASS = os.environ['MASTODON_PASS']

CLIENTCRED_FILENAME = 'pytooter_clientcred.secret'

def login():
    clientcred_file = os.path.join(MASTODON_CREDPATH, CLIENTCRED_FILENAME)
    if not os.path.isfile(clientcred_file):
        # create an application (this info is kept at the server side) only once
        Mastodon.create_app(
             MASTODON_APPNAME,
             api_base_url = MASTODON_INSTANCE,
             to_file = clientcred_file
        )

    mastodon = Mastodon(
        client_id = clientcred_file,
        api_base_url = MASTODON_INSTANCE
    )
    mastodon.log_in(
        MASTODON_USER,
        MASTODON_PASS,
        # to_file = ... (could cache credentials for next time)
    )
    return mastodon


def send_toot():
    with session_scope() as session:
        now = datetime.datetime.utcnow()
        yesterday = now - datetime.timedelta(days=1)

        next_pull_request = (
            session
                .query(PullRequests)
                .order_by(PullRequests.merged_at.asc())
                .filter(PullRequests.merged_at > yesterday)
                .filter(PullRequests.toot_id.is_(None))
                .filter(PullRequests.merged_at.isnot(None))
                .first()
        )
        if next_pull_request is None:
            return
        mastodon = login()

        commits_url = 'https://api.github.com/repos/bitcoin/bitcoin/commits'
        params = {'author': next_pull_request.author.login}
        response = requests.get(commits_url, params=params)
        response_json = response.json()

        if len(response_json) > 1:
            status = 'Merged PR from {0}: {1} {2}' \
                .format(next_pull_request.author.login,
                        next_pull_request.title,
                        next_pull_request.html_url)
        else:
            status = '''
            {0}'s first merged PR: {1}
            Congratulations!  🎉🍾🎆
            '''.format(next_pull_request.author.login,
                       next_pull_request.html_url)
        toot = mastodon.toot(status)
        new_tweet = Toots()
        new_tweet.id = toot['id']
        new_tweet.pull_request_id = next_pull_request.number
        session.add(new_tweet)
        next_pull_request.toot_id = toot['id']


if __name__ == '__main__':
    send_toot()
