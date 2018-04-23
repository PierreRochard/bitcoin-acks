import json
import logging
import os
from pprint import pformat
from typing import Tuple

import requests
import time
from requests import HTTPError

logging.basicConfig(level=logging.DEBUG)

class GitHubData(object):
    api_url = 'https://api.github.com/'
    user_name = os.environ.get('GITHUB_USER')
    password = os.environ.get('GITHUB_API_TOKEN')

    @property
    def _auth(self) -> Tuple[str, str]:
        return self.user_name, self.password

    def graphql_post(self, json_object: dict):
        try:
            r = requests.post(self.api_url + 'graphql',
                              auth=self._auth,
                              json=json_object)
            r.raise_for_status()
        except HTTPError as e:
            logging.warning(e)
            time.sleep(60)
            r = self.graphql_post(json_object=json_object)
        return r

    def get_pull_requests(self):
        with open('pull_requests.graphql', 'r') as query_file:
            query = query_file.read()

        pull_requests = []
        results = True
        last_cursor = None
        variables = None
        while results:
            if last_cursor is not None:
                variables = {
                    'prCursor': last_cursor
                }
            json_object = {
                'query': query,
                'variables': variables
            }

            data = self.graphql_post(json_object=json_object).json()

            logging.info(msg=pformat(data['data']['rateLimit']))

            total_to_fetch = data['data']['repository']['pullRequests']['totalCount']

            results = data['data']['repository']['pullRequests']['edges']
            pull_requests.extend(results)
            last_cursor = pull_requests[-1]['cursor']

            logging.info(msg=(len(pull_requests), total_to_fetch))

            with open('pull_requests.json', 'w') as output_file:
                json.dump(pull_requests, output_file, indent=4, sort_keys=True)


if __name__ == '__main__':
    GitHubData().get_pull_requests()
