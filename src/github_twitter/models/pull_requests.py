from sqlalchemy import Column, DateTime, Integer, String

from github_twitter.database.base import Base


class PullRequests(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime, nullable=False)

    repository_id = Column(Integer, nullable=False)
    tweet_id = Column(Integer, nullable=True, unique=True)
