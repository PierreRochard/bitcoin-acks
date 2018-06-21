import os
from git import Repo


class Repository(object):
    def __init__(self, repository_path: str, repository_name: str):
        if not os.path.exists(repository_name):
            os.mkdir(repository_name)
            url = 'https://github.com/{repository_path}/{repository_name}'.format(repository_path=repository_path, repository_name=repository_name)
            Repo.clone_from(url, repository_name)
        repo = Repo(repository_name)
        remote_names = [r.name for r in repo.remotes]
        # if 'upstream' not in remote_names:
        #     repo.create_remote('upstream', )
        # upstream = repo.remote('upstream')
        # upstream.fetch()


        print(repo)

if __name__ == '__main__':
    Repository('bitcoin', 'bitcoin')
