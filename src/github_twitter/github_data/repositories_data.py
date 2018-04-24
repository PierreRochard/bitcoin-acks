from typing import List

import requests
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.github_data import GitHubData
from github_twitter.models import Repositories


class RepositoriesData(GitHubData):
    def __init__(self, repository_path: str, repository_name: str):
        super(RepositoriesData, self).__init__()
        with session_scope() as session:
            try:
                repository = (
                    session.query(Repositories)
                        .filter(
                        and_(
                            Repositories.path == repository_path,
                            Repositories.name == repository_name
                        )
                    )
                        .one()
                )
            except NoResultFound:
                repository = Repositories()
                repository.path = repository_path
                repository.name = repository_name
                session.add(repository)
                session.flush()
            session.expunge(repository)
        self.repo = repository
