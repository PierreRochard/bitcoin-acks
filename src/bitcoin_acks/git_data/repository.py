import os
from git import Repo

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.database import session_scope
from bitcoin_acks.models import PullRequests


class Repository(object):
    def __init__(self, repository_path: str, repository_name: str):
        self.repository_path = repository_path
        self.repository_name = repository_name
        if not os.path.exists(repository_name):
            os.mkdir(repository_name)
            url = 'https://github.com/{repository_path}/{repository_name}'.format(repository_path=repository_path, repository_name=repository_name)
            Repo.clone_from(url, repository_name)
        self.repo = Repo(repository_name)
        remote_names = [r.name for r in self.repo.remotes]
        # if 'upstream' not in remote_names:
        #     repo.create_remote('upstream', )
        # upstream = repo.remote('upstream')
        # upstream.fetch()
        print(self.repo)

    def add_remote(self, name: str, url: str):
        self.repo.create_remote(name=name, url=url)

    def fetch_remote(self, name: str):
        remote = self.repo.remote(name=name)
        remote.fetch()

    def sync_open_pull_requests(self):
        with session_scope() as session:
            pull_requests = (
                session
                .query(PullRequests.head_repository_name,
                       PullRequests.head_repository_url)
                .filter(PullRequests.state == PullRequestState.OPEN.value)
                .group_by(PullRequests.head_repository_url)
                .all()
            )
            for head_repository_url, head_repository_name in pull_requests:
                self.add_remote(name=pull_request.head_repository_name,
                                url=pull_request.head_repository_url)
                self.fetch_remote(name=pull_request.head_repository_name)


if __name__ == '__main__':
    Repository('bitcoin', 'bitcoin').sync_open_pull_requests()
