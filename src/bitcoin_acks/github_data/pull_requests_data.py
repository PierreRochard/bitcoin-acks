import logging
from pprint import pformat
from typing import List

import os
import requests
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

    def get_all(self, state: str = None) -> List[dict]:
        path = os.path.dirname(os.path.abspath(__file__))
        graphql_file = os.path.join(path, 'pull_requests.graphql')
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

            for item in results:
                self.upsert(item)
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

            author = data.pop('author', None)
            comments = data.pop('comments', None)
            commits = data.pop('commits', None)
            labels = data.pop('labels', None)

            if author:
                author_login = author['login']
                user_id = UsersData().upsert(data=author)
                record.author_id = user_id
            else:
                author_login = None

            for key, value in data.items():
                setattr(record, key, value)

            # Last commit is used to determine CI status
            record.commit_count = commits['totalCount']
            if commits['nodes']:
                last_commit = commits['nodes'][0]['commit']
                last_commit_status = last_commit.get('status')
                if last_commit_status:
                    record.last_commit_state = last_commit_status['state'].capitalize()
                    descriptions = [s['description'] for s in last_commit_status['contexts']]
                    record.last_commit_state_description = ', '.join(descriptions)

            for label in labels['nodes']:
                LabelsData.upsert(pull_request_id=record.id, data=label)

            record.comment_count = 0
            if comments:
                record.comment_count = comments['totalCount']
                ack_comment_authors = []
                comments = comments['nodes']
                comments = sorted(comments, key=lambda k: k['publishedAt'], reverse=True)
                for comment in comments:
                    if comment['author'] is None:
                        continue
                    comment_author_name = comment['author']['login']
                    if (comment_author_name != author_login
                            and comment_author_name not in ack_comment_authors):
                        is_ack = CommentsData().upsert(pull_request_id=record.id,
                                                       data=comment)
                        if is_ack:
                            ack_comment_authors.append(comment_author_name)
                record.ack_comment_count = len(ack_comment_authors)

            diff = requests.get(record.diff_url).text
            DiffsData().insert(record.id, diff)

    def update_database(self, state: str = None):
        data = self.get_all(state=state)
        for item in data:
            self.upsert(item)


if __name__ == '__main__':

    PullRequestsData('bitcoin', 'bitcoin').update_database(
        state='OPEN'
    )
