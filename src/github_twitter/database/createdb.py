from github_twitter.database.session import session_scope
from github_twitter.database.base import Base

import github_twitter.models


def create_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.create_all(session.connection())


def drop_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.drop_all(session.connection())


if __name__ == '__main__':
    drop_database()
    create_database()
