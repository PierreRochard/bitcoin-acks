import string

import dateparser
import json
import requests
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.session_scope import session_scope
from github_twitter.models import PullRequests
from github_twitter.models.responses import Responses


def insert_pull_request(event):
    pull_request_id = event['payload']['number']
    with session_scope() as session:
        try:
            (
                session
                    .query(PullRequests)
                    .filter(PullRequests.id == pull_request_id)
                    .one()
            )
        except NoResultFound:
            new_record = PullRequests()
            new_record.id = pull_request_id
            new_record.author = event['payload']['pull_request']['user']['login']
            new_record.title = event['payload']['pull_request']['title']
            new_record.url = event['payload']['pull_request']['html_url']
            new_record.created_at = dateparser.parse(event['payload']['pull_request']['created_at'])
            new_record.merged_at = dateparser.parse(event['payload']['pull_request']['merged_at'])
            session.add(new_record)


def insert_response():
    with session_scope() as session:
        last_response = (
            session
                .query(Responses)
                .order_by(Responses.timestamp.desc())
                .first()
        )
        if last_response is None:
            headers = None
        else:
            headers = {'If-None-Match': last_response.etag}

        repo_events_url = 'https://api.github.com/repos/bitcoin/bitcoin/events?page=1&per_page=300'
        events_response = requests.get(repo_events_url, headers=headers)
        if events_response.status_code == 304:
            return
        new_response = Responses()
        new_response.etag = events_response.headers['etag']
        session.add(new_response)

        events = events_response.json()

        punctuation_translator = str.maketrans('', '', string.punctuation)
        sanitized_etag = events_response.headers['etag'].translate(punctuation_translator)
        # Todo: fix so this doesn't fill up the entire disk....
        # with open('{0}.json'.format(sanitized_etag), 'w') as outfile:
        #     json.dump(events, outfile)

        for event in events:
            if event['type'] == 'PullRequestEvent':
                if event['payload']['pull_request']['merged']:
                    insert_pull_request(event)


if __name__ == '__main__':
    insert_response()
