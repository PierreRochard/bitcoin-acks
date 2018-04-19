from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.github_data import GitHubData
from github_twitter.models import Users


class UsersData(GitHubData):

    @staticmethod
    def upsert(data: dict):
        with session_scope() as session:
            try:
                user_record = (
                    session.query(Users)
                        .filter(Users.id == data['id'])
                        .one()
                )
            except NoResultFound:
                user_record = Users()
                session.add(user_record)
            for key, value in data.items():
                setattr(user_record, key, value)
            session.commit()
