import json
import pytest

from github_twitter.services.github import GitHubService


class TestGitHubService(object):
    def test_get_pull_requests(self, repository):
        pull_requests = GitHubService().get_pull_requests(name=repository.name, path=repository.path)
        assert len(pull_requests)
        for pull_request in pull_requests:
            assert 'merged_at' in pull_request.keys()
            assert pull_request['user']['login']
            assert pull_request['title']
            assert pull_request['html_url']
            assert pull_request['created_at']
            assert pull_request['number']

    @pytest.mark.issues
    def test_get_issues(self, repository):
        page = 1
        issues = []
        while True:
            try:
                new_issues = GitHubService().get_issues(name=repository.name, path=repository.path, since=None, page=page, direction='desc')
                if not new_issues:
                    break
                issues.extend(new_issues)
                with open('issues_example.json', 'w') as outfile:
                    json.dump(issues, outfile, indent=4, sort_keys=True)
                page += 1
            except:
                raise
