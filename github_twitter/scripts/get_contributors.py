from pprint import pformat

import requests

# contributors_url = 'https://api.github.com/repos/bitcoin/bitcoin/contributors'
# params = {'anon': 1}
# response = requests.get(contributors_url, params=params)
# response_json = response.json()

# contributors_url = 'https://api.github.com/repos/bitcoin/bitcoin/stats/contributors'
# response = requests.get(contributors_url)
# response_json = response.json()

from git import Repo

repo = Repo('/Users/pierrerochard/src/bitcoin')
commits = list(repo.iter_commits('master'))

authors = []
for commit in commits:
    authors.append((commit.author.name, commit.author.email))

authors = set(authors)
print(pformat(authors))
print(len(authors))
