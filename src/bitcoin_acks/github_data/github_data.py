import json
import logging
import os
from typing import Tuple

import backoff
import requests

from bitcoin_acks.logging import log

logging.basicConfig(level=logging.ERROR)
logging.getLogger('backoff').setLevel(logging.INFO)


def fatal_code(e):
    # We only retry if the error was "Bad Gateway"
    log.error('GitHub error', fatal_code=e)
    return e.response.status_code != 502


class GitHubData(object):
    api_url = 'https://api.github.com/'
    user_name = os.environ['GITHUB_USER']
    password = os.environ['GITHUB_API_TOKEN']

    dev_preview_headers = {
        'Accept': 'application/vnd.github.starfox-preview+json'
    }

    @property
    def auth(self) -> Tuple[str, str]:
        return self.user_name, self.password

    def get_graphql_schema(self):
        r = requests.get(
            self.api_url + 'graphql',
            auth=self.auth,
            headers=self.dev_preview_headers
        )
        r.raise_for_status()
        with open('graphql.schema.json', 'w') as output_file:
            json.dump(r.json(), output_file, indent=4, sort_keys=True)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        giveup=fatal_code
    )
    def graphql_post(self, json_object: dict):
        log.debug('graphql post', api_url=self.api_url, json=json_object)
        r = requests.post(
            self.api_url + 'graphql',
            auth=self.auth,
            headers=self.dev_preview_headers,
            json=json_object
        )
        log.debug('graphql post response', response=r.headers)
        r.raise_for_status()
        return r


if __name__ == '__main__':
    GitHubData().get_graphql_schema()
