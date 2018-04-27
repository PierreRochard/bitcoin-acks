import json
import pytest
from collections import defaultdict

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from bitcoin_acks.models import PullRequests
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
         '_links': {'value_type': 'dict',
                    'nested_properties': {'comments': {'value_type': 'dict'},
                                          'commits': {'value_type': 'dict'},
                                          'html': {'value_type': 'dict'},
                                          'issue': {'value_type': 'dict'},
                                          'review_comment': {'value_type': 'dict'},
                                          'review_comments': {'value_type': 'dict'},
                                          'self': {'value_type': 'dict'},
                                          'statuses': {'value_type': 'dict'}}},
         'assignee': {'value_type': 'dict',
                      'nested_properties': {'avatar_url': {'value_type': 'str'},
                                            'events_url': {'value_type': 'str'},
                                            'followers_url': {'value_type': 'str'},
                                            'following_url': {'value_type': 'str'},
                                            'gists_url': {'value_type': 'str'},
                                            'gravatar_id': {'value_type': 'str'},
                                            'html_url': {'value_type': 'str'},
                                            'id': {'value_type': 'int'},
                                            'login': {'value_type': 'str'},
                                            'organizations_url': {'value_type': 'str'},
                                            'received_events_url': {
                                                'value_type': 'str'},
                                            'repos_url': {'value_type': 'str'},
                                            'site_admin': {'value_type': 'bool'},
                                            'starred_url': {'value_type': 'str'},
                                            'subscriptions_url': {'value_type': 'str'},
                                            'type': {'value_type': 'str'},
                                            'url': {'value_type': 'str'}},
                      'nullable': True}, 'assignees': {'value_type': 'list'},
         'author_association': {'value_type': 'str'}, 'base': {'value_type': 'dict',
                                                               'nested_properties': {
                                                                   'label': {
                                                                       'value_type': 'str'},
                                                                   'ref': {
                                                                       'value_type': 'str'},
                                                                   'repo': {
                                                                       'value_type': 'dict'},
                                                                   'sha': {
                                                                       'value_type': 'str'},
                                                                   'user': {
                                                                       'value_type': 'dict'}}},
         'body': {'value_type': 'str', 'nullable': True},
         'closed_at': {'nullable': True, 'value_type': 'str'},
         'comments_url': {'value_type': 'str'}, 'commits_url': {'value_type': 'str'},
         'created_at': {'value_type': 'str'}, 'diff_url': {'value_type': 'str'},
         'head': {'value_type': 'dict',
                  'nested_properties': {'label': {'value_type': 'str'},
                                        'ref': {'value_type': 'str'},
                                        'repo': {'value_type': 'dict'},
                                        'sha': {'value_type': 'str'},
                                        'user': {'value_type': 'dict'}}},
         'html_url': {'value_type': 'str'}, 'id': {'value_type': 'int'},
         'issue_url': {'value_type': 'str'}, 'labels': {'value_type': 'list'},
         'locked': {'value_type': 'bool'},
         'merge_commit_sha': {'value_type': 'str', 'nullable': True},
         'merged_at': {'nullable': True, 'value_type': 'str'},
         'milestone': {'nullable': True, 'value_type': 'dict',
                       'nested_properties': {'closed_at': {'value_type': 'str'},
                                             'closed_issues': {'value_type': 'int'},
                                             'created_at': {'value_type': 'str'},
                                             'creator': {'value_type': 'dict'},
                                             'description': {'value_type': 'str'},
                                             'due_on': {'nullable': True},
                                             'html_url': {'value_type': 'str'},
                                             'id': {'value_type': 'int'},
                                             'labels_url': {'value_type': 'str'},
                                             'number': {'value_type': 'int'},
                                             'open_issues': {'value_type': 'int'},
                                             'state': {'value_type': 'str'},
                                             'title': {'value_type': 'str'},
                                             'updated_at': {'value_type': 'str'},
                                             'url': {'value_type': 'str'}}},
         'number': {'value_type': 'int'}, 'patch_url': {'value_type': 'str'},
         'requested_reviewers': {'value_type': 'list'},
         'requested_teams': {'value_type': 'list'},
         'review_comment_url': {'value_type': 'str'},
         'review_comments_url': {'value_type': 'str'}, 'state': {'value_type': 'str'},
         'statuses_url': {'value_type': 'str'}, 'title': {'value_type': 'str'},
         'updated_at': {'value_type': 'str'}, 'url': {'value_type': 'str'},
         'user': {'value_type': 'dict',
                  'nested_properties': {'avatar_url': {'value_type': 'str'},
                                        'events_url': {'value_type': 'str'},
                                        'followers_url': {'value_type': 'str'},
                                        'following_url': {'value_type': 'str'},
                                        'gists_url': {'value_type': 'str'},
                                        'gravatar_id': {'value_type': 'str'},
                                        'html_url': {'value_type': 'str'},
                                        'id': {'value_type': 'int'},
                                        'login': {'value_type': 'str'},
                                        'organizations_url': {'value_type': 'str'},
                                        'received_events_url': {'value_type': 'str'},
                                        'repos_url': {'value_type': 'str'},
                                        'site_admin': {'value_type': 'bool'},
                                        'starred_url': {'value_type': 'str'},
                                        'subscriptions_url': {'value_type': 'str'},
                                        'type': {'value_type': 'str'},
                                        'url': {'value_type': 'str'}}}
        }

        properties = defaultdict(dict)
        for pull_request in pull_requests_data:
            for key, value in pull_request.items():
                value_type = str(type(value).__name__)
                if value is None:
                    properties[key]['nullable'] = True
                    continue
                elif (properties[key].get('value_type', False) and
                      properties[key]['value_type'] != value_type):
                    raise Exception(f'inconsistent type for {key}')
                else:
                    properties[key]['value_type'] = value_type
                    if value_type == 'dict':
                        properties[key]['nested_properties'] = defaultdict(dict)
                        for nested_key, nested_value in value.items():
                            nested_value_type = str(type(nested_value).__name__)
                            if nested_value is None:
                                properties[key]['nested_properties'][nested_key]['nullable'] = True
                                continue
                            elif (properties[key]['nested_properties'][nested_key].get('value_type', False) and
                                  properties[key]['nested_properties'][nested_key]['value_type'] != nested_value_type):
                                raise Exception(f'inconsistent type for {key}/{nested_key}')
                            else:
                                properties[key]['nested_properties'][nested_key]['value_type'] = nested_value_type

        assert properties == expected_properties

    @pytest.mark.unit_pull_requests
    def test_pull_requests_data_update(self, repository, pull_requests_data):

        prs = PullRequestsData(repository_name=repository.name,
                               repository_path=repository.path)
        for data in pull_requests_data[0:100]:
            prs.upsert(data)

        with session_scope() as session:
            records = (
                session.query(PullRequests).all()
            )
            assert len(records) == 100