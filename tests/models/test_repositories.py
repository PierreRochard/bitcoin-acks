import json

from mock import mock
import pytest

from github_twitter.database.session_scope import session_scope
from github_twitter.models import PullRequests, Issues

with open('issues_example.json', 'r') as outfile:
    issues = json.load(outfile)


class TestRepositories(object):
    def test_insert_pull_requests(self, repository):
        repository.insert_pull_requests()
        with session_scope() as session:
            pull_requests = (
                session.query(PullRequests).all()
            )
            assert len(pull_requests)

    # @pytest.mark.issues
    @mock.patch('github_twitter.services.github.GitHubService.get_issues', return_value=issues)
    def test_insert_issues(self, mock_github_service, repository):
        repository.insert_issues()
        with session_scope() as session:
            inserted_issues = (
                session.query(Issues).all()
            )
            assert len(inserted_issues)
