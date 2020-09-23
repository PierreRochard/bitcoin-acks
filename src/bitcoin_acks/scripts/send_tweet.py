import datetime
import os

import requests
from twython import Twython

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import PullRequests
from bitcoin_acks.models.tweets import Tweets


def send_tweet(pull_request_number=None):
    with session_scope() as session:
        now = datetime.datetime.utcnow()
        yesterday = now - datetime.timedelta(days=1)
        twitter = Twython(os.environ['BTC_TWITTER_APP_KEY'],
                          os.environ['BTC_TWITTER_APP_SECRET'],
                          os.environ['BTC_TWITTER_OAUTH_TOKEN'],
                          os.environ['BTC_TWITTER_OAUTH_TOKEN_SECRET']
                          )
        if pull_request_number:
            next_pull_request = (
                session
                    .query(PullRequests)
                    .filter(PullRequests.number == pull_request_number)
                .first()
            )
        else:
            next_pull_request = (
                session
                    .query(PullRequests)
                    .order_by(PullRequests.merged_at.asc())
                    .filter(PullRequests.merged_at > yesterday)
                    .filter(PullRequests.tweet_id.is_(None))
                    .filter(PullRequests.merged_at.isnot(None))
                    .first()
            )
        if next_pull_request is None:
            log.debug('No pull requests found.')
            return
        commits_url = 'https://api.github.com/repos/bitcoin/bitcoin/commits'
        params = {'author': next_pull_request.author.login}
        response = requests.get(commits_url, params=params)
        log.debug('github response', response=response)
        response_json = response.json()
        author_name = next_pull_request.author.name or next_pull_request.author.login
        if len(response_json) > 1 and next_pull_request.number != 14802:
            status = 'Merged PR from {0}: {1} {2}' \
                .format(author_name,
                        next_pull_request.title,
                        next_pull_request.html_url)
        else:
            status = '''
            {0}'s first merged PR: {1}
            Congratulations!  🎉🍾🎆
            '''.format(author_name,
                       next_pull_request.html_url)
        log.debug('tweet status', status=status)
        tweet = twitter.update_status(status=status)
        log.debug('tweet', tweet=tweet)
        new_tweet = Tweets()
        new_tweet.id = tweet['id']
        new_tweet.pull_request_id = next_pull_request.number
        session.add(new_tweet)
        next_pull_request.tweet_id = tweet['id']


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tweet merged pull request')
    parser.add_argument('-p',
                        dest='pr_number',
                        type=int,
                        default=None)
    args = parser.parse_args()
    log.debug(f'sending tweet for {args.pr_number}')
    send_tweet(pull_request_number=args.pr_number)
