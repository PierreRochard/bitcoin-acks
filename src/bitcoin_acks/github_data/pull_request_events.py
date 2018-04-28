from datetime import datetime

import math
import requests
import time

from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from bitcoin_acks.github_data.repositories_data import RepositoriesData

import sys; print(sys.path)

class PullRequestEvents(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(PullRequestEvents, self).__init__(repository_path=repository_path,
                                                repository_name=repository_name)
        self.etag = None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def get(self):
        url = self.api_url + 'repos/{0}/{1}/events?page=1&per_page=300'.format(
            self.repo.path,
            self.repo.name
        )
        headers = {}
        if self.etag is not None:
            headers['If-None-Match'] = self.etag
        response = requests.get(url, auth=self.auth, headers=headers)
        if response.status_code == 304:
            return
        response.raise_for_status()
        self.etag = response.headers['etag']
        self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        self.rate_limit_reset = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))

        events = response.json()
        pull_request_numbers = set()
        for event in events:
            pr = (event['payload'].get('pull_request', None)
                  or event['payload'].get('issue', None)
                  )
            if pr is not None and ('base' in pr.keys() or 'pull_request' in pr.keys()):
                pull_request_numbers.add(pr['number'])

        pr_data = PullRequestsData(repository_path=self.repo.path,
                                   repository_name=self.repo.name)
        for number in pull_request_numbers:
            pr_data.update(number=number)


if __name__ == '__main__':
    pr_events = PullRequestEvents('bitcoin', 'bitcoin')
    while True:
        pr_events.get()
        sleep_time = (datetime.utcnow() - pr_events.rate_limit_reset).seconds/pr_events.rate_limit_remaining
        time.sleep(math.ceil(sleep_time))
        print(pr_events.etag, sleep_time)
