import os
import subprocess

from git import Repo, CommandError
from sqlalchemy import func

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.database.session import session_scope
from bitcoin_acks.models.pull_requests import PullRequests


class Repository(object):
    def __init__(self, repository_path: str, repository_name: str):
        self.repository_path = repository_path
        self.repository_name = repository_name
        self.local_repo_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', self.repository_name))
        self.diffs_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', 'diffs'))
        if not os.path.exists(self.local_repo_path):
            os.mkdir(self.local_repo_path)
            url = 'https://github.com/{repository_path}/{repository_name}'.format(repository_path=repository_path, repository_name=repository_name)
            Repo.clone_from(url, self.local_repo_path)
        self.repo = Repo(self.local_repo_path)
        remote_names = [r.name for r in self.repo.remotes]
        # if 'upstream' not in remote_names:
        #     repo.create_remote('upstream', )
        # upstream = repo.remote('upstream')
        # upstream.fetch()
        print(self.repo)

    def add_remote(self, name: str, url: str):
        try:
            self.repo.create_remote(name=name, url=url)
        except CommandError:
            return

    def create_diff(self, remote_repo_name: str, ref_name: str,
                    ref_old_hash: str, ref_new_hash: str):
        if ref_old_hash is None:
            file = f'{self.diffs_path}/{remote_repo_name}_{ref_name.replace("/", "_")}_{ref_new_hash}.html'
            command_arg = f'{remote_repo_name}/{ref_name}/{ref_new_hash}^...{remote_repo_name}/{ref_name}/{ref_new_hash}'
        else:
            file = f'{remote_repo_name}_{ref_name}_{ref_old_hash}_{ref_new_hash}.html'
            command_arg = f'{remote_repo_name}/{ref_name}/{ref_old_hash}..{remote_repo_name}/{ref_name}/{ref_new_hash}'
        command = ['diff2html', '-F',
                   file,
                   '--',
                   '-M',
                   command_arg
                   ]
        print(' '.join(command))
        try:
            subprocess.run(command, check=True, cwd=self.local_repo_path)
        except Exception as exc:
            print(exc)

    def fetch_remote(self, name: str):
        remote = self.repo.remote(name=name)
        try:
            remote.fetch()
        except CommandError:
            return

    def create_remote_branch_head(self,
                                  remote_repo_name: str,
                                  remote_ref_name: str):
        remote = self.repo.remote(name=remote_repo_name)
        for ref in remote.refs:
            if ref.name == f'{remote_repo_name}/{remote_ref_name}':
                branch_name = f'{ref.name}/{ref.object.hexsha}'
                branch = remote.repo.create_head(path=branch_name, commit=ref.name)

    def sync_pull_requests(self,
                           pull_request_id: str = None,
                           state: PullRequestState = None):

        with session_scope() as session:
            query = (
                session
                .query(PullRequests.head_repository_name,
                       PullRequests.head_repository_url,
                       func.array_agg(PullRequests.head_ref_name))
                .group_by(PullRequests.head_repository_name, PullRequests.head_repository_url)
            )
            if pull_request_id is not None:
                query = query.filter(PullRequests.id == pull_request_id)
            elif state is not None:
                query = query.filter(PullRequests.state == state.value)

            head_repositories = query.all()
            for head_repository_name, head_repository_url, refs in head_repositories:
                self.add_remote(name=head_repository_name,
                                url=head_repository_url)
                self.fetch_remote(name=head_repository_name)
                for ref in refs:
                    self.create_remote_branch_head(remote_repo_name=head_repository_name,
                                                   remote_ref_name=ref)


if __name__ == '__main__':
    Repository('bitcoin', 'bitcoin').sync_pull_requests(state=PullRequestState.OPEN)
