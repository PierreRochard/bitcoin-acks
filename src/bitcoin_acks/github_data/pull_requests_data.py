from pprint import pformat
from typing import List
import logging
import os

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.comments_data import CommentsData
from bitcoin_acks.github_data.diffs_data import DiffsData
from bitcoin_acks.github_data.labels_data import LabelsData
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.github_data.users_data import UsersData
from bitcoin_acks.models import PullRequests


class PullRequestsData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(PullRequestsData, self).__init__(repository_path=repository_path,
                                               repository_name=repository_name)

    def get(self, number: int) -> dict:
        path = os.path.dirname(os.path.abspath(__file__))
        graphql_file = os.path.join(path, 'graphql_queries', 'pull_request.graphql')
        with open(graphql_file, 'r') as query_file:
            query = query_file.read()

        json_object = {
            'query': query,
            'variables': {'prNumber': number}
        }
        data = self.graphql_post(json_object=json_object).json()

        return data['data']['repository']['pullRequest']

    def get_all(self, state: str = None):
        path = os.path.dirname(os.path.abspath(__file__))
        graphql_file = os.path.join(path, 'graphql_queries', 'pull_requests.graphql')
        with open(graphql_file, 'r') as query_file:
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

            logging.info(msg=(last_cursor, len(pull_requests), total_to_fetch))

            for pull_request in results:
                self.upsert_nested_data(pull_request)

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

            for key, value in data.items():
                setattr(record, key, value)

    def upsert_nested_data(self, pull_request: dict):
        author_data = pull_request.pop('author')
        if author_data is not None:
            pull_request['author_id'] = UsersData().upsert(data=author_data)

        comments_data = pull_request.pop('comments')
        pull_request['comment_count'] = comments_data['totalCount']
        pull_request['ack_comment_count'] = CommentsData().bulk_upsert(
            pull_request_id=pull_request['id'],
            comments=comments_data['nodes'])

        # Last commit is used to determine CI status
        last_commit_status = None
        commits = pull_request.pop('commits')
        pull_request['commit_count'] = commits['totalCount']
        if commits['nodes']:
            last_commit = commits['nodes'][0]['commit']
            last_commit_status = last_commit.get('status')

        if last_commit_status is not None:
            pull_request['last_commit_state'] = last_commit_status['state'].capitalize()
            descriptions = [s['description'] for s in last_commit_status['contexts']]
            pull_request['last_commit_state_description'] = ', '.join(descriptions)

        labels = pull_request.pop('labels')
        for label in labels['nodes']:
            LabelsData.upsert(pull_request_id=pull_request['id'], data=label)

        DiffsData().get(repository_path=self.repo.path,
                        repository_name=self.repo.name,
                        pull_request_number=pull_request['number'],
                        pull_request_id=pull_request['id'])

        self.upsert(pull_request)

    def update_all(self, state: str = None):
        self.get_all(state=state)

    def update(self, number: int):
        data = self.get(number=number)
        self.upsert_nested_data(data)


if __name__ == '__main__':
    PullRequestsData('bitcoin', 'bitcoin').update_all(
        # state='OPEN'
    )
