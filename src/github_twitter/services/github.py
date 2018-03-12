from typing import List

import os
import requests
from datetime import datetime, timedelta, timezone


class GitHubService(object):
    api_url = 'https://api.github.com/'
    user_name = os.environ.get('GITHUB_USER')
    password = os.environ.get('GITHUB_API_TOKEN')

    @classmethod
    def get(cls, url, params):
        response = requests.get(url=url, params=params, auth=(cls.user_name, cls.password))
        if response.status_code != 200:
            raise Exception()
        return response.json()

    def get_merged_pull_requests(self, path: str, name: str):
        pull_requests = self.get_pull_requests(path=path, name=name)
        pull_requests = [pr for pr in pull_requests if pr['merged_at']]
        return pull_requests

    def get_pull_requests(self,
                          path: str,
                          name: str,
                          state: str = 'closed',
                          sort: str = 'updated',
                          direction: str = 'desc',
                          page: int = 1,
                          per_page: int = 100):
        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'page': page,
            'per_page': per_page
        }
        url = '{api_url}repos/{path}/{name}/pulls'.format(api_url=self.api_url,
                                                          path=path,
                                                          name=name)
        response = self.get(url, params)
        return sorted(response, key=lambda k: k['updated_at'], reverse=True)

    def get_issues(self,
                   path: str,
                   name: str,
                   state: str = 'all',
                   sort: str = 'updated',
                   direction: str = 'desc',
                   since: [int, None] = None,
                   page: int = 1) -> List[dict]:

        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'page': page
        }
        if since is not None:
            since = datetime.utcnow() - timedelta(days=since)
            since = since.replace(tzinfo=timezone.utc)
            since = since.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['since'] = since

        url = '{api_url}repos/{path}/{name}/issues'.format(api_url=self.api_url,
                                                           path=path,
                                                           name=name)

        response = self.get(url=url, params=params)
        issues = sorted(response, key=lambda k: k['updated_at'], reverse=True)
        issues = [i for i in issues if not i.get('pull_request')]
        return issues
