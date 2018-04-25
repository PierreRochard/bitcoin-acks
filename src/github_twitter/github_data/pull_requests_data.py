import json
import logging
from pprint import pformat
from typing import List

import re
import requests
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.comments_data import CommentsData
from github_twitter.github_data.diffs_data import DiffsData
from github_twitter.github_data.repositories_data import RepositoriesData
from github_twitter.github_data.users_data import UsersData
from github_twitter.models import PullRequests


class PullRequestsData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(PullRequestsData, self).__init__(repository_path=repository_path,
                                               repository_name=repository_name)

    def get_all(self, state: str = None) -> List[dict]:
        with open('pull_requests.graphql', 'r') as query_file:
            query = query_file.read()

        pull_requests = []
        last_cursor = None
        variables = {}
        while True:
            if last_cursor is not None:
                variables['prCursor'] = last_cursor
            if state is not None:
                variables['prState'] = state

            json_object = {
                'query': query,
                'variables': variables
            }

            data = self.graphql_post(json_object=json_object).json()

            logging.info(msg=pformat(data['data']['rateLimit']))

            total_to_fetch = data['data']['repository']['pullRequests']['totalCount']

            results = data['data']['repository']['pullRequests']['edges']
            if not len(results):
                break
            last_cursor = results[-1]['cursor']
            results = [r['node'] for r in results]
            pull_requests.extend(results)

            logging.info(msg=(len(pull_requests), total_to_fetch))

            with open('pull_requests.json', 'w') as output_file:
                json.dump(pull_requests, output_file, indent=4, sort_keys=True)
        return pull_requests

    def upsert(self, data: dict):
        with session_scope() as session:
            try:
                record = (
                    session
                        .query(PullRequests)
                        .filter(
                            and_(PullRequests.repository_id == self.repo.id,
                                 PullRequests.number == data['number'])
                        )
                        .one()
                )
            except NoResultFound:
                record = PullRequests()
                record.repository_id = self.repo.id
                record.number = data['number']
                session.add(record)

            author = data.pop('author')
            comments = data.pop('comments')
            commits = data.pop('commits')
            record.commit_count = commits['totalCount']
            last_commit = commits['nodes'][0]['commit']
            last_commit_status = last_commit.get('status')
            if last_commit_status:
                record.last_commit_state = last_commit_status['state'].capitalize()
                descriptions = [s['description'] for s in last_commit_status['contexts']]
                record.last_commit_state_description = ', '.join(descriptions)

            labels = data.pop('labels')

            user_id = UsersData().upsert(data=author)
            record.author_id = user_id
            record.comments_count = comments['totalCount']

            for key, value in data.items():
                setattr(record, key, value)

            for comment in comments['nodes']:
                CommentsData().upsert(pull_request_id=record.id,
                                      data=comment)

            diff = requests.get(record.diff_url).text
            DiffsData().insert(record.id, diff)

    def update_database(self, state: str = None):
        data = self.get_all(state=state)
        for item in data:
            self.upsert(item)


if __name__ == '__main__':
    PullRequestsData('bitcoin', 'bitcoin').update_database(state='OPEN')
