from typing import List

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.repositories_data import RepositoriesData
from github_twitter.github_data.users_data import UsersData
from github_twitter.models import PullRequests


class PullRequestsData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(PullRequestsData, self).__init__(repository_path=repository_path,
                                               repository_name=repository_name)

    def get(self,
            state: str = 'all',
            sort: str = 'updated',
            direction: str = 'desc',
            page: int = 1,
            per_page: int = 100) -> List[dict]:

        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'page': page,
            'per_page': per_page
        }
        response = self._get(path='pulls', params=params)
        pull_requests_data = sorted(response,
                                    key=lambda k: k['updated_at'],
                                    reverse=True)
        return pull_requests_data

    def get_all(self, state: str = 'all') -> List[dict]:
        pull_requests_data = []
        page = 1
        while True:
            data = self.get(state=state, page=page)
            if not data:
                break
            pull_requests_data.extend(data)
            page += 1
        return pull_requests_data

    def upsert(self, data: dict):
        with session_scope() as session:
            try:
                pull_request_record = (
                    session
                        .query(PullRequests)
                        .filter(
                            and_(PullRequests.repository_id == self.repo.id,
                                 PullRequests.number == data['number'])
                        )
                        .one()
                )
            except NoResultFound:
                pull_request_record = PullRequests()
                pull_request_record.repository_id = self.repo.id
                pull_request_record.number = data['number']
                session.add(pull_request_record)

            links = data.pop('_links')
            assignee = data.pop('assignee')
            assignees = data.pop('assignees')
            base = data.pop('base')
            head = data.pop('head')
            labels = data.pop('labels')
            milestone = data.pop('milestone')
            requested_reviewers = data.pop('requested_reviewers')
            requested_teams = data.pop('requested_teams')
            user = data.pop('user')

            UsersData.upsert(data=user)

            pull_request_record.user_id = user['id']

            for key, value in data.items():
                setattr(pull_request_record, key, value)

    def update_database(self):
        data = self.get_all()
        for item in data:
            self.upsert(item)


if __name__ == '__main__':
    PullRequestsData('bitcoin', 'bitcoin').update_database()
