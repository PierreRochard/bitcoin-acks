import os

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.constants import PullRequestState
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

    def get_all(self,
                state: PullRequestState = None,
                newest_first: bool = False,
                limit: int = None):
        path = os.path.dirname(os.path.abspath(__file__))
        graphql_file = os.path.join(path, 'graphql_queries', 'pull_requests.graphql')
        with open(graphql_file, 'r') as query_file:
            query = query_file.read()

        first_cursor = None
        last_cursor = None
        variables = {}
        received = 0
        while limit is None or received < limit:

            if limit is None:
                quantity = 100
            else:
                quantity = min(limit - received, 100)

            if last_cursor is not None and not newest_first:
                variables['prCursorAfter'] = last_cursor
            elif last_cursor is not None and newest_first:
                variables['prCursorBefore'] = first_cursor

            if newest_first:
                variables['prFirst'] = None
                variables['prLast'] = quantity
            else:
                variables['prFirst'] = quantity
                variables['prLast'] = None

            if state is not None:
                variables['prState'] = state.value

            json_object = {
                'query': query,
                'variables': variables
            }

            data = self.graphql_post(json_object=json_object).json()

            results = data['data']['repository']['pullRequests']['edges']

            if not len(results):
                break

            last_cursor = results[-1]['cursor']
            first_cursor = results[0]['cursor']
            results = [r['node'] for r in results]

            for pull_request in results:
                if limit is not None and received == limit:
                    break
                yield pull_request
                received += 1

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
        reviews_data = pull_request.pop('reviews')
        pull_request['comment_count'] = comments_data['totalCount']
        comments_and_reviews = comments_data['nodes'] + reviews_data['nodes']
        pull_request['ack_comment_count'] = CommentsData().bulk_upsert(
            pull_request_id=pull_request['id'],
            comments=comments_and_reviews)

        # Last commit is used to determine CI status
        last_commit_status = None
        last_commit_short_hash = None
        commits = pull_request.pop('commits')
        pull_request['commit_count'] = commits['totalCount']
        if commits['nodes']:
            last_commit = commits['nodes'][0]['commit']
            last_commit_status = last_commit.get('status')
            last_commit_short_hash = last_commit['oid'][0:7]

        if last_commit_status is not None:
            pull_request['last_commit_state'] = last_commit_status['state'].capitalize()
            descriptions = [s['description'] for s in last_commit_status['contexts']]
            pull_request['last_commit_state_description'] = ', '.join(descriptions)
            pull_request['last_commit_short_hash'] = last_commit_short_hash

        labels = pull_request.pop('labels')
        for label in labels['nodes']:
            LabelsData.upsert(pull_request_id=pull_request['id'], data=label)

        DiffsData().get(repository_path=self.repo.path,
                        repository_name=self.repo.name,
                        pull_request_number=pull_request['number'],
                        pull_request_id=pull_request['id'])

        self.upsert(pull_request)

    def update_all(self,
                   state: PullRequestState = None,
                   newest_first: bool = False,
                   limit: int = None):

        for pull_request in self.get_all(state=state,
                                         newest_first=newest_first,
                                         limit=limit):
            self.upsert_nested_data(pull_request)

    def update(self, number: int):
        data = self.get(number=number)
        self.upsert_nested_data(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Update pull request')
    parser.add_argument('-s',
                        dest='state',
                        type=str,
                        choices=['OPEN', 'CLOSED', 'MERGED'],
                        default=None
                        )
    parser.add_argument('-l',
                        dest='limit',
                        type=int,
                        default=None
                        )
    parser.add_argument('-n',
                        dest='newest_first',
                        action='store_true',
                        default=False)
    parser.add_argument('-p',
                        dest='pr_number',
                        type=int,
                        default=None)
    args = parser.parse_args()
    pull_requests_data = PullRequestsData('bitcoin', 'bitcoin')

    if args.pr_number is not None:
        pull_requests_data.update(number=args.pr_number)

    else:
        # Transform state into enum element
        if args.state is not None:
            args.state = PullRequestState[args.state]

        pull_requests_data.update_all(state=args.state,
                                      newest_first=args.newest_first,
                                      limit=args.limit)
