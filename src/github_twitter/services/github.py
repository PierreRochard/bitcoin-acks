import requests


class GitHubService(object):
    api_url = 'https://api.github.com/'

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

        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            raise Exception()
        return sorted(response.json(), key=lambda k: k['updated_at'], reverse=True)
