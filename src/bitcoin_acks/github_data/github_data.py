import json
import logging
import os
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
    def auth(self) -> Tuple[str, str]:
        return self.user_name, self.password

    def get_graphql_schema(self):
        r = requests.get(self.api_url + 'graphql',
                         auth=self.auth)
        r.raise_for_status()
        with open('graphql_schema.json', 'w') as output_file:
            json.dump(r.json(), output_file, indent=4, sort_keys=True)

    def graphql_post(self, json_object: dict):
        try:
            r = requests.post(self.api_url + 'graphql',
                              auth=self.auth,
                              json=json_object)
            r.raise_for_status()
        except HTTPError as e:
            logging.warning(e)
            time.sleep(60)
            r = self.graphql_post(json_object=json_object)
        return r


if __name__ == '__main__':
    GitHubData().get_graphql_schema()
