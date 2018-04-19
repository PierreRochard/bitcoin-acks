from typing import List

from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.repositories_data import RepositoriesData
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
        pull_request_id = data['number']
        with session_scope() as session:
            try:
                pull_request_record = (
                    session
                        .query(PullRequests)
                        .filter(PullRequests.id == pull_request_id)
                        .one()
                )
            except NoResultFound:
                pull_request_record = PullRequests()
                pull_request_record.repository_id = self.repo.id
                pull_request_record.id = pull_request_id
                pull_request_record.url = data['html_url']
                pull_request_record.author = data['user']['login']
                pull_request_record.created_at = data['created_at']
                session.add(pull_request_record)

            pull_request_record.title = data['title']
            pull_request_record.merged_at = data['merged_at']

    def update_database(self):
        data = self.get_all()
        for item in data:
            self.upsert(item)
