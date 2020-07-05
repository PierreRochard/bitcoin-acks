import sys
from datetime import date, datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.data_schemas import pull_request_schema
from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.comments_data import CommentsData
from bitcoin_acks.github_data.diffs_data import DiffsData
from bitcoin_acks.github_data.graphql_queries import (
    pull_request_graphql_query,
    pull_requests_graphql_query
)
from bitcoin_acks.github_data.labels_data import LabelsData
from bitcoin_acks.github_data.polling_data import PollingData
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.github_data.users_data import UsersData
from bitcoin_acks.models import PullRequests


class PullRequestsData(RepositoriesData):

    MAX_PRS = 20

    def __init__(self, repository_path: str, repository_name: str):
        super(PullRequestsData, self).__init__(repository_path=repository_path,
                                               repository_name=repository_name)

    def get(self, number: int) -> dict:

        json_object = {
            'query': pull_request_graphql_query,
            'variables': {'prNumber': number}
        }
        data = self.graphql_post(json_object=json_object).json()
        pull_request = data['data']['repository']['pullRequest']
        deserialized_data = pull_request_schema.load(pull_request)
        return deserialized_data

    def get_all(self,
                state: PullRequestState = None,
                limit: int = None,
                newer_than: date = None):
        """
        Generator: starting from the most recent to the oldest, yield one PR at a time
        """
        last_cursor = None
        variables = {}
        received = 0
        while limit is None or received < limit:

            if limit is None:
                variables['prFirst'] = self.MAX_PRS
            else:
                variables['prFirst'] = min(limit - received, self.MAX_PRS)

            if state is not None:
                variables['prState'] = state.value

            variables['prCursorAfter'] = last_cursor
            variables['searchQuery'] = f'updated:>{newer_than} repo:bitcoin/bitcoin'

            json_object = {
                'query': pull_requests_graphql_query,
                'variables': variables
            }

            data = self.graphql_post(json_object=json_object).json()

            results = data['data']['search']['edges']

            if not len(results):
                break

            last_cursor = results[-1]['cursor']
            results = [r['node'] for r in results]
            for pull_request in results:
                if limit is not None and received == limit:
                    break

                deserialized_data = pull_request_schema.load(pull_request)
                if deserialized_data:
                    yield deserialized_data
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

    @staticmethod
    def update_review_count_cache(pull_request_id: str, pull_request_author_id: str):
        review_count = CommentsData.get_review_count(pull_request_id=pull_request_id,
                                                     pull_request_author_id=pull_request_author_id)
        with session_scope() as session:
            record = (
                session
                    .query(PullRequests)
                    .filter(PullRequests.id == pull_request_id)
                    .one()
            )
            record.review_decisions_count = review_count

    def upsert_nested_data(self, pull_request: dict):
        author = pull_request.pop('author')
        if author is not None:
            pull_request['author_id'] = UsersData().upsert(data=author)

        comments_data = CommentsData(repository_name=self.repo.name,
                                     repository_path=self.repo.path)
        comments = pull_request.pop('comments')
        reviews = pull_request.pop('reviews')
        if comments['totalCount'] > 100 or reviews['totalCount'] > 100:
            comments_and_reviews = [c for c in comments_data.get_all(
                pull_request_number=pull_request['number'])]
        else:
            comments_and_reviews = comments['nodes'] + reviews['nodes']

        project_cards = pull_request.pop('projectCards')
        blocker_card = [c for c in project_cards['nodes'] if
                        c['column'] and c['column']['name'] == 'Blockers']
        if blocker_card and not pull_request['closedAt']:
            pull_request['is_high_priority'] = blocker_card[0]['createdAt']
        else:
            pull_request['is_high_priority'] = None

        timeline_items = pull_request.pop('timelineItems')
        blocker_events = [e for e in timeline_items['nodes'] if
                          e['projectColumnName'] == 'Blockers']
        for blocker_event in blocker_events:
            if blocker_event['typename'] == 'AddedToProjectEvent':
                pull_request['added_to_high_priority'] = blocker_event['createdAt']
            elif blocker_event['typename'] == 'RemovedFromProjectEvent':
                pull_request['removed_from_high_priority'] = blocker_event['createdAt']

        # Last commit is used to determine CI status
        last_commit_status = None
        commits = pull_request.pop('commits')
        pull_request['commit_count'] = commits['totalCount']
        head_commit_hash = pull_request['headRefOid']
        if commits['nodes']:
            last_commit = [c for c in commits['nodes'] if c['commit']['oid'] == head_commit_hash][0]['commit']
            last_commit_status = last_commit.get('status')

        if last_commit_status is not None:
            pull_request['last_commit_state'] = last_commit_status['state'].capitalize()
            descriptions = [s['description'] for s in last_commit_status['contexts']]
            pull_request['last_commit_state_description'] = ', '.join(descriptions)

        if len(commits['nodes']):
            pull_request['last_commit_short_hash'] = commits['nodes'][-1]['commit']['oid'][0:7]
            pull_request['last_commit_pushed_date'] = commits['nodes'][-1]['commit']['pushedDate']

        LabelsData.delete(pull_request_id=pull_request['id'])
        labels = pull_request.pop('labels')
        for label in labels['nodes']:
            LabelsData.upsert(pull_request_id=pull_request['id'], data=label)

        DiffsData().get(repository_path=self.repo.path,
                        repository_name=self.repo.name,
                        pull_request_number=pull_request['number'],
                        pull_request_id=pull_request['id'])

        self.upsert(pull_request)
        comments_data.bulk_upsert(pull_request_id=pull_request['id'],
                                  comments=comments_and_reviews)
        self.update_review_count_cache(pull_request_id=pull_request['id'],
                                       pull_request_author_id=pull_request.get('author_id'))

    def update_all(self,
                   state: PullRequestState = None,
                   limit: int = None,
                   newer_than: date = None):

        for pull_request in self.get_all(state=state,
                                         limit=limit,
                                         newer_than=newer_than):
            self.upsert_nested_data(pull_request)

    def update(self, number: int):
        data = self.get(number=number)
        self.upsert_nested_data(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Update pull request')
    parser.add_argument('-p',
                        dest='pr_number',
                        type=int,
                        default=None)
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
    parser.add_argument('-hp',
                        dest='high_priority',
                        type=bool,
                        default=False)
    parser.add_argument('-o',
                        dest='old',
                        type=bool,
                        default=True)
    args = parser.parse_args()

    pull_requests_data = PullRequestsData('bitcoin', 'bitcoin')
    polling_data = PollingData('github')

    if polling_data.is_polling():
        print('GitHub is already being polled')
        sys.exit(0)

    polling_data.start()

    if args.pr_number is not None:
        pull_requests_data.update(number=args.pr_number)
    elif args.state is not None:
        args.state = PullRequestState[args.state]
        pull_requests_data.update_all(state=args.state,
                                      limit=args.limit)
    elif args.high_priority:
        with session_scope() as session:
            record = (
                session
                    .query(PullRequests.number)
                    .filter(
                    and_(PullRequests.is_high_priority.isnot(None))
                )
                    .all()
            )
            for r in record:
                pull_requests_data.update(number=int(r.number))
    elif args.old:
        with session_scope() as session:
            try:
                record = (
                    session
                    .query(PullRequests.updated_at)
                    .order_by(PullRequests.updated_at.desc())
                    .limit(1)
                    .one()
                )
                from_date = record.updated_at.date() - timedelta(days=1)
            except NoResultFound:
                from_date = date(2000, 1, 1)
            pull_requests_data.update_all(newer_than=from_date,
                                          limit=args.limit)
    else:
        # All
        pull_requests_data.update_all(limit=args.limit)

    polling_data.stop()
