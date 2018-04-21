from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    select, func, and_)
from sqlalchemy.orm import relationship

from github_twitter.database.base import Base
from github_twitter.models.diffs import Diffs
from github_twitter.models.users import Users


class PullRequests(Base):
    __tablename__ = 'pull_requests'
    __table_args__ = (UniqueConstraint('number',
                                       'repository_id',
                                       name='pull_requests_unique_constraint'),
                      )

    id = Column(Integer, primary_key=True)

    author_association = Column(String, nullable=False)
    body = Column(String)
    closed_at = Column(DateTime)
    comments_url = Column(String, nullable=False)
    commits_url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    diff_url = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    issue_url = Column(String, nullable=False)
    locked = Column(Boolean, nullable=False)
    merge_commit_sha = Column(String, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    number = Column(Numeric, nullable=False)
    patch_url = Column(String, nullable=False)
    review_comment_url = Column(String, nullable=False)
    review_comments_url = Column(String, nullable=False)
    state = Column(String, nullable=False)
    statuses_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)

    repository_id = Column(Integer, nullable=False)
    user_id = Column(Numeric, nullable=False)
    tweet_id = Column(Integer, nullable=True, unique=True)

    user = relationship(Users,
                        primaryjoin=user_id == Users.id,
                        foreign_keys='[PullRequests.user_id]',
                        backref='pull_requests'
                        )

    diff = relationship(Diffs,
                        primaryjoin=and_(id == Diffs.pull_request_id,
                                         Diffs.is_most_recent.is_(True)),
                        foreign_keys=[Diffs.pull_request_id],
                        backref='pull_request',
                        uselist=False
                        )
