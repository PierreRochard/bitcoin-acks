import json

import pytest

from bitcoin_acks.github_data.issues_data import IssuesData
from tests import issues_file_path


class TestIssuesData(object):

    @pytest.mark.integration
    @pytest.mark.github
    @pytest.mark.issues
    def test_get_issues(self, repository):
        issues = IssuesData(repository_name=repository.name,
                            repository_path=repository.path).get_all()
        with open(issues_file_path, 'w') as outfile:
            json.dump(issues, outfile, indent=4, sort_keys=True)

    @pytest.mark.unit
    @pytest.mark.github
    @pytest.mark.issues
    def test_pull_requests_data_properties(self, issues_data):
        expected_properties = {
            'assignee',
            'assignees',
            'author_association',
            'body',
            'closed_at',
            'comments',
            'comments_url',
            'created_at',
            'events_url',
            'html_url',
            'id',
            'labels',
            'labels_url',
            'locked',
            'milestone',
            'number',
            'pull_request',
            'repository_url',
            'state',
            'title',
            'updated_at',
            'url',
            'user'
        }
        properties = set()
        for issue in issues_data:
            properties = properties.union(issue.keys())
        unexpected_properties = properties ^ expected_properties
        assert not unexpected_properties
