from github_twitter.database.session_scope import session_scope
from github_twitter.models import PullRequests


class TestRepositories(object):
    def test_insert_pull_requests(self, repository):
        repository.insert_pull_requests()
        with session_scope() as session:
            pull_requests = (
                session.query(PullRequests).all()
            )
            assert len(pull_requests)
