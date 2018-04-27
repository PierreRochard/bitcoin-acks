import json
import logging
from typing import List

import pytest

from tests import issues_file_path, pull_requests_file_path


@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    monkeypatch.setattr('github_twitter.database.session.is_test', True)
    from bitcoin_acks.database.createdb import create_database, drop_database
    drop_database(echo=False)
    create_database(echo=False)


@pytest.fixture
def repository():
    from bitcoin_acks.models.repositories import Repositories
    from bitcoin_acks.database.session import session_scope
    r = Repositories()
    r.path = 'bitcoin'
    r.name = 'bitcoin'
    with session_scope() as session:
        session.add(r)
        session.flush()
        session.expunge(r)
    return r


@pytest.fixture(scope="session")
def issues_data() -> List[dict]:
    with open(issues_file_path, 'r') as outfile:
        issues = json.load(outfile)
        return issues


@pytest.fixture(scope="session")
def pull_requests_data() -> List[dict]:
    with open(pull_requests_file_path, 'r') as outfile:
        pull_requests = json.load(outfile)
        return pull_requests
