from typing import List

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.models import Issues, Milestones, Users


class IssuesData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(IssuesData, self).__init__(repository_path=repository_path,
                                         repository_name=repository_name)

    def get(self,
            state: str = 'all',
            sort: str = 'updated',
            direction: str = 'desc',
            since: [int, None] = None,
            page: int = 1) -> List[dict]:

        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'page': page
        }
        if since is not None:
            since = datetime.utcnow() - timedelta(days=since)
            since = since.replace(tzinfo=timezone.utc)
            since = since.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['since'] = since

        response = self._get(path='issues', params=params)
        issues = [i for i in response if not i.get('pull_request')]
        issues = sorted(issues,
                        key=lambda k: k['updated_at'],
                        reverse=True)
        return issues

    def get_all(self, state: str = 'all') -> List[dict]:
        issues_data = []
        page = 1
        while True:
            issues = self.get(state=state, page=page)
            if not issues:
                break
            issues_data.extend(issues)
            page += 1
        return issues_data

    def upsert(self, data: dict):
        issue_id = data['id']
        with session_scope() as session:
            try:
                issue_record = (
                    session.query(Issues)
                        .filter(and_(Issues.id == issue_id,
                                     Issues.repository_id == self.id))
                        .one()
                )
            except NoResultFound:
                issue_record = Issues()
                session.add(issue_record)
            for key, value in data.items():
                if hasattr(issue_record, key):
                    column_type = getattr(Issues,
                                          key).expression.type.python_type
                    if column_type == datetime and value is not None:
                        value = value
                    setattr(issue_record, key, value)
            if data['milestone']:
                issue_record.milestone_id = Milestones.insert_milestone(
                    data['milestone'])
            issue_record.repository_id = self.repo.id
            issue_record.user_id = Users.insert_user(data['user'])
            # Todo: add labels and assignees
            session.commit()

    def update_database(self):
        data = self.get_all()
        for item in data:
            self.upsert(item)
