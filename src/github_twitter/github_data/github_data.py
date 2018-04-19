import os
from typing import Tuple


class GitHubData(object):
    api_url = 'https://api.github.com/'
    user_name = os.environ.get('GITHUB_USER')
    password = os.environ.get('GITHUB_API_TOKEN')

    @property
    def _auth(self) -> Tuple[str, str]:
        return self.user_name, self.password
