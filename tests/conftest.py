import json
import logging
from typing import List

import pytest

from tests import issues_file_path, pull_requests_file_path, \
    pull_request_file_path
from tests.test_cases import pull_requests_get_all_test_cases


@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    monkeypatch.setattr('bitcoin_acks.database.session.is_test', True)
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


@pytest.fixture(scope='session')
def issues_data() -> List[dict]:
    with open(issues_file_path, 'r') as outfile:
        issues = json.load(outfile)
        return issues


@pytest.fixture(scope='session')
def pull_requests_data() -> List[dict]:
    data = []

    try:
        with open(pull_request_file_path, 'r') as outfile:
            pr = json.load(outfile)
            data.append(pr)
    except FileNotFoundError:
        pass

    for test_case in pull_requests_get_all_test_cases:
        state, limit = test_case
        file_path = pull_requests_file_path.format(state=str(state),
                                                   limit=str(limit))
        try:
            with open(file_path, 'r') as outfile:
                pull_requests = json.load(outfile)
                data.extend(pull_requests)
        except FileNotFoundError:
            pass

    if not len(data):
        raise Warning('no pull request test data available')

    return data


@pytest.fixture(scope='session')
def valid_pr_number() -> int:
    return 10757
