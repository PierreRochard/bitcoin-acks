from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean)
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.base import Base
from github_twitter.database.session_scope import session_scope


class Users(Base):
    __tablename__ = 'users'

    html_url = Column(String)
    id = Column(Integer, primary_key=True)
    login = Column(String)
    type = Column(String)
    twitter_handle = Column(String)

    @staticmethod
    def insert_user(user: dict):
        with session_scope() as session:
            try:
                user_record = (
                    session.query(Users)
                        .filter(Users.id == user['id'])
                        .one()
                )
            except NoResultFound:
                user_record = Users()
                session.add(user_record)
            for key, value in user.items():
                if hasattr(user_record, key):
                    setattr(user_record, key, value)
            session.commit()
        return user['id']
