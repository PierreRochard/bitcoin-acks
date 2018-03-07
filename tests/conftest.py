import logging
import os

import pytest

from github_twitter.database.session_scope import get_db_path


@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    monkeypatch.setattr('github_twitter.database.session_scope.database_file',
                        'test_github_twitter.db')
    try:
        os.remove(get_db_path())
    except OSError:
        pass

    from github_twitter.database.createdb import create_database
    create_database(echo=False)


@pytest.fixture
def repository():
    from github_twitter.models.repositories import Repositories
    from github_twitter.database.session_scope import session_scope
    r = Repositories()
    r.path = 'bitcoin'
    r.name = 'bitcoin'
    with session_scope() as session:
        session.add(r)
        session.flush()
        session.expunge(r)
    return r
