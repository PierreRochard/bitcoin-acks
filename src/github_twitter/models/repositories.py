import dateparser
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.base import Base
from github_twitter.database.session_scope import session_scope
from github_twitter.models.pull_requests import PullRequests
from github_twitter.services.github import GitHubService


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    name = Column(String)

    def insert_pull_requests(self):
        pull_requests = GitHubService().get_merged_pull_requests(path=self.path, name=self.name)
        for pull_request in pull_requests:
            pull_request_id = pull_request['number']
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
                    # Todo: add repository ID
                    new_record.id = pull_request_id
                    new_record.author = pull_request['user']['login']
                    new_record.title = pull_request['title']
                    new_record.url = pull_request['html_url']
                    new_record.created_at = dateparser.parse(pull_request['created_at'])
                    new_record.merged_at = dateparser.parse(pull_request['merged_at'])
                    session.add(new_record)
