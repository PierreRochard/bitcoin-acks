# User Stories
### Bitcoin ACKs v1 
- [x] As a reviewer I want to see which PRs have “momentum” (concept acks from contributors) so that I can prioritize and best use my review time.
- [x] As a maintainer I want to see which PRs are merge candidates so that I don’t have to wait for authors to ping me or spend time individually analysing PRs.
- [x] As an author I want to see when my PRs are conflicted or not building on Travis so that I can rebase.

### Bitcoin ACKs v2
- [ ] ~As a reviewer I want to see an inter-diff between force-pushed commits so that I can focus on code I have not already reviewed.~ [GitHub implemented this!](https://github.blog/changelog/2018-11-15-force-push-timeline-event/)
- [ ] ~~As an author I want to receive a notification when my PR becomes conflicted so that I can rebase.~~ [DrahtBot](https://github.com/DrahtBot) solves this!
- [ ] ~~As an author, reviewer, or maintainer I want to see which PRs would become conflicted after a PR is merged so that I can coordinate and prioritize.~~  [DrahtBot](https://github.com/DrahtBot) solves this!

### Bitcoin ACKs v3
- [ ] As an author or reviewer I want to have online C++ Jupyter notebooks so that I can explore, reason about, and communicate problems in an interactive manner.



# Contributing


### Installing the App

- [Install the Postgres RDBMS](https://www.postgresql.org/download/)

- Install Python 3.6

- Create a virtual environment, install the requirements, and activate the virtual environment:
```
$ python3.6 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ source env/bin/activate
```

- Switch to the postgres user and enter the Postgres shell:
```
$ sudo su - postgres
$ psql
```

- Create development and test databases:
```
postgres=# create database bitcoin_acks;
postgres=# create database bitcoin_acks_test;
```

- Set password for the `postgres` user:
```
postgres=# \password
postgres=# \q
```

- [Create GitHub API token](https://github.com/settings/tokens/new) 
  The token must have the `public_repo` permission scope.

- Export the following variables to your environment.
```
GH_PGDATABASE=bitcoin_acks
TEST_GH_PGDATABASE=bitcoin_acks_test
PGUSER=postgres
PGPASSWORD=<your password>
PGHOST=127.0.0.1
PGPORT=5432
GITHUB_USER=<you-github-username>
GITHUB_API_TOKEN=<your-github-api-token>
```

- Create database tables:
```
$ python src/bitcoin_acks/database/createdb.py
```

- Populate the database
```
$ python src/bitcoin_acks/github_data/pull_requests_data.py
```

### Running the App

- Poll the Github API to keep the database up to date:
```
$ python src/bitcoin_acks/github_data/pull_request_events.py
```

- Run the web server:
```
$ python src/bitcoin_acks/webapp/run.py
```

### Upgrading

- Run migrations:
```
$ alembic --config src/bitcoin_acks/migrations/alembic.ini upgrade head
```


### Running the tests
```
$ python setup.py test
```
