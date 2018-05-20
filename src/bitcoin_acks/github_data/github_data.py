import json
import logging
import os
from typing import Tuple

import backoff
import requests

logging.basicConfig(level=logging.ERROR)
logging.getLogger('backoff').setLevel(logging.INFO)


def fatal_code(e):
    # We only retry if the error was "Bad Gateway"
    return e.response.status_code != 502


class GitHubData(object):
    api_url = 'https://api.github.com/'
    user_name = os.environ['GITHUB_USER']
    password = os.environ['GITHUB_API_TOKEN']

    @property
    def auth(self) -> Tuple[str, str]:
        return self.user_name, self.password

    def get_graphql_schema(self):
        r = requests.get(self.api_url + 'graphql',
                         auth=self.auth)
        r.raise_for_status()
        with open('graphql_schema.json', 'w') as output_file:
            json.dump(r.json(), output_file, indent=4, sort_keys=True)

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          giveup=fatal_code)
    def graphql_post(self, json_object: dict):
        r = requests.post(self.api_url + 'graphql',
                          auth=self.auth,
                          json=json_object)
        r.raise_for_status()
        return r


if __name__ == '__main__':
    GitHubData().get_graphql_schema()
