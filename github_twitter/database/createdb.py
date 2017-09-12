from github_twitter.database.session_scope import session_scope
from github_twitter.database.base import Base

import github_twitter.models


def setup_database():
    with session_scope(echo=True) as session:
        Base.metadata.drop_all(session.connection())
        Base.metadata.create_all(session.connection())


if __name__ == '__main__':
    setup_database()
