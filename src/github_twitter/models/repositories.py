from datetime import datetime

import dateparser
from sqlalchemy import Column, String, Integer, and_
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.base import Base
from github_twitter.database.session_scope import session_scope
from github_twitter.models.pull_requests import PullRequests
from github_twitter.models.users import Users
from github_twitter.models.milestones import Milestones
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

    def insert_issues(self):
        from github_twitter.models.issues import Issues
        page = 1
        while True:
            issues = GitHubService().get_issues(path=self.path, name=self.name, page=page)
            page += 1
            print(page, len(issues))
            # if not issues:
            #     break
            for issue in issues:
                issue_id = issue['id']
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
                    for key, value in issue.items():
                        if hasattr(issue_record, key):
                            column_type = getattr(Issues, key).expression.type.python_type
                            if column_type == datetime and value is not None:
                                value = dateparser.parse(value)
                            setattr(issue_record, key, value)
                    if issue['milestone']:
                        issue_record.milestone_id = Milestones.insert_milestone(issue['milestone'])
                    issue_record.repository_id = self.id
                    issue_record.user_id = Users.insert_user(issue['user'])
                    # Todo: add labels and assignees
                    session.commit()
