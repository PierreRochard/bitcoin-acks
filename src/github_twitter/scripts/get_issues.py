from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.session import session_scope
from github_twitter.models import Repositories


def get_issues():
    with session_scope() as session:
        try:
            repository = (
                session.query(Repositories)
                    .filter(
                    and_(
                        Repositories.name == 'bitcoin',
                        Repositories.path == 'bitcoin'
                    )
                )
                    .one()
            )
        except NoResultFound:
            repository = Repositories()
            repository.path = 'bitcoin'
            repository.name = 'bitcoin'
            session.add(repository)
            session.flush()
        session.expunge(repository)
    repository.insert_issues()


if __name__ == '__main__':
    get_issues()
