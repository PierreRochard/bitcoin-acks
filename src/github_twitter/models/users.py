from sqlalchemy import (
    Column,
    String
)

from github_twitter.database.base import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    login = Column(String, unique=True)

    avatar_url = Column(String)
    name = Column(String)
    bio = Column(String)
    url = Column(String)

    twitter_handle = Column(String)
