import json

import pytest

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.data_schemas import pull_request_schema
from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from tests import pull_request_file_path, pull_requests_file_path
from tests.test_cases import pull_requests_get_all_test_cases


class TestPullRequestsData(object):

    @pytest.mark.populate_fixtures
    @pytest.mark.integration_pull_requests
    def test_get(self, repository, valid_pr_number):
        pr_data = PullRequestsData(repository_name=repository.name,
                                   repository_path=repository.path)
        pr = pr_data.get(number=valid_pr_number)
        assert pr
        with open(pull_request_file_path, 'w') as outfile:
            json.dump(pr, outfile, indent=4, sort_keys=True)

    @pytest.mark.populate_fixtures
    @pytest.mark.integration_pull_requests
    @pytest.mark.parametrize(
        'state, limit',
        pull_requests_get_all_test_cases
    )
    def test_get_all(self, repository, state: PullRequestState, limit):
        pr_data = PullRequestsData(repository_name=repository.name,
                                   repository_path=repository.path)

        prs = []
        for pr in pr_data.get_all(state=state, limit=limit):
            if prs:
                assert prs[-1]['updatedAt'] > pr['updatedAt']
            if state is not None:
                assert pr['state'] == state.value
            prs.append(pr)

        assert len(prs) == limit
        file_path = pull_requests_file_path.format(state=str(state),
                                                   limit=str(limit))
        with open(file_path, 'w') as outfile:
            serialized_data, errors = pull_request_schema.dump(prs, many=True)
            json.dump(serialized_data, outfile, indent=4, sort_keys=True)

    @pytest.mark.unit_pull_requests
    def test_pull_requests_data_validation(self, pull_requests_data):
        deserialized_data, errors = pull_request_schema.load(pull_requests_data, many=True)
        assert not errors
