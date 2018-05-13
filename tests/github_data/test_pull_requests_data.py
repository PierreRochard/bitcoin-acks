import json

import pytest

from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from tests import pull_request_file_path, pull_requests_file_path
from tests.data_schemas.pull_request_schema import PullRequestSchema
from tests.test_cases import pull_requests_get_all_test_cases


class TestPullRequestsData(object):

    @pytest.mark.populate_fixtures
    @pytest.mark.integration_pull_requests
    def test_get(self, repository, valid_pr_number):
        pr_data = PullRequestsData(repository_name=repository.name,
                                   repository_path=repository.path)
        pr = pr_data.get(number=valid_pr_number)
        assert len(pr.keys()) == 16
        with open(pull_request_file_path, 'w') as outfile:
            json.dump(pr, outfile, indent=4, sort_keys=True)

    @pytest.mark.populate_fixtures
    @pytest.mark.integration_pull_requests
    @pytest.mark.parametrize(
        'state, newest_first, limit',
        pull_requests_get_all_test_cases
    )
    def test_get_all(self, repository, state, newest_first, limit):
        pr_data = PullRequestsData(repository_name=repository.name,
                                   repository_path=repository.path)
        prs = pr_data.get_all(state=state,
                              newest_first=newest_first,
                              limit=limit)
        for pr in prs:
            assert len(pr.keys()) == 16
        file_path = pull_requests_file_path.format(state=str(state),
                                                   newest_first=str(newest_first),
                                                   limit=str(limit))
        with open(file_path, 'w') as outfile:
            json.dump(prs, outfile, indent=4, sort_keys=True)

    @pytest.mark.unit_pull_requests
    def test_pull_requests_data_validation(self, pull_requests_data):
        deserialized_data, errors = PullRequestSchema().load(pull_requests_data, many=True)
        assert not errors
