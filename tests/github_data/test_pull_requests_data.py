import json
import pytest
from collections import defaultdict

from github_twitter.github_data.pull_requests_data import PullRequestsData
from tests import pull_requests_file_path


class TestPullRequestsData(object):

    @pytest.mark.integration_pull_requests
    def test_get_pull_requests(self, repository):
        pull_requests = PullRequestsData(
            repository_name=repository.name,
            repository_path=repository.path).get_all()
        with open(pull_requests_file_path, 'w') as outfile:
            json.dump(pull_requests, outfile, indent=4, sort_keys=True)

    @pytest.mark.unit_pull_requests
    def test_pull_requests_data_properties(self, pull_requests_data):
        expected_properties = {
            '_links',
            'assignee',
            'assignees',
            'author_association',
            'base',
            'body',
            'closed_at',
            'comments_url',
            'commits_url',
            'created_at',
            'diff_url',
            'head',
            'html_url',
            'id',
            'issue_url',
            'labels',
            'locked',
            'merge_commit_sha',
            'merged_at',
            'milestone',
            'number',
            'patch_url',
            'requested_reviewers',
            'requested_teams',
            'review_comment_url',
            'review_comments_url',
            'state',
            'statuses_url',
            'title',
            'updated_at',
            'url',
            'user'
        }
        properties = set()
        for pull_request in pull_requests_data:
            properties = properties.union(pull_request.keys())
        unexpected_properties = properties ^ expected_properties
        assert not unexpected_properties

    @pytest.mark.unit_pull_requests
    def test_pull_requests_data_types(self, pull_requests_data):
        expected_properties = {
            '_links': {'value_type': 'dict'},
            'assignee': {'value_type': 'dict',
                         'nullable': True},
            'assignees': {'value_type': 'list'},
            'author_association': {'value_type': 'str'},
            'base': {'value_type': 'dict'},
            'body': {'value_type': 'str', 'nullable': True},
            'closed_at': {'nullable': True,
                          'value_type': 'str'},
            'comments_url': {'value_type': 'str'},
            'commits_url': {'value_type': 'str'},
            'created_at': {'value_type': 'str'},
            'diff_url': {'value_type': 'str'},
            'head': {'value_type': 'dict'},
            'html_url': {'value_type': 'str'},
            'id': {'value_type': 'int'},
            'issue_url': {'value_type': 'str'},
            'labels': {'value_type': 'list'},
            'locked': {'value_type': 'bool'},
            'merge_commit_sha': {'value_type': 'str',
                                 'nullable': True},
            'merged_at': {'nullable': True,
                          'value_type': 'str'},
            'milestone': {'nullable': True,
                          'value_type': 'dict'},
            'number': {'value_type': 'int'},
            'patch_url': {'value_type': 'str'},
            'requested_reviewers': {'value_type': 'list'},
            'requested_teams': {'value_type': 'list'},
            'review_comment_url': {'value_type': 'str'},
            'review_comments_url': {'value_type': 'str'},
            'state': {'value_type': 'str'},
            'statuses_url': {'value_type': 'str'},
            'title': {'value_type': 'str'},
            'updated_at': {'value_type': 'str'},
            'url': {'value_type': 'str'},
            'user': {'value_type': 'dict'}
        }

        properties = defaultdict(dict)
        for pull_request in pull_requests_data:
            for key, value in pull_request.items():
                value_type = str(type(value).__name__)
                if value is None:
                    properties[key]['nullable'] = True
                    continue
                elif properties[key].get('value_type', False) and \
                        properties[key]['value_type'] != value_type:
                    raise Exception(f'inconsistent type for {key}')
                else:
                    properties[key]['value_type'] = value_type
        assert properties == expected_properties
