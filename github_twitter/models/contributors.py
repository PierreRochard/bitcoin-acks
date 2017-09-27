from sqlalchemy import Column, Integer, String

from github_twitter.database.base import Base


class Contributors(Base):
    __tablename__ = 'contributors'

    id = Column(Integer, primary_key=True)
    contributions = Column(Integer, nullable=False)
    github_name = Column(String, nullable=False, unique=True)
    twitter_name = Column(String, unique=True)
