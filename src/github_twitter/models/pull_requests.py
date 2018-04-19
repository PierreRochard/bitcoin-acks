from sqlalchemy import Column, DateTime, Integer, String, Numeric, Boolean

from github_twitter.database.base import Base


class PullRequests(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)

    number = Column(Numeric, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    state = Column(String, nullable=False)
    locked = Column(Boolean, nullable=False)

    html_url = Column(String, nullable=False)
    diff_url = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime, nullable=False)

    author_user_id = Column(Numeric, nullable=False)
    repository_id = Column(Integer, nullable=False)
    tweet_id = Column(Integer, nullable=True, unique=True)
