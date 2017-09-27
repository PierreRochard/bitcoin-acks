from sqlalchemy import Column, Integer, String

from github_twitter.database.base import Base


class Contributors(Base):
    __tablename__ = 'contributors'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    git_name = Column(String, unique=True)
    github_name = Column(String, unique=True)
    twitter_name = Column(String, unique=True)
