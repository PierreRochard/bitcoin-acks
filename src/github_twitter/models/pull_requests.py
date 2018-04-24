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

    id = Column(String, primary_key=True)

    additions = Column(Integer)
    body = Column(String)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    deletions = Column(Integer)
    merged_at = Column(DateTime, nullable=True)
    number = Column(Numeric, nullable=False)
    state = Column(String, nullable=False)
    title = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    repository_id = Column(Integer, nullable=False)
    author_id = Column(String, nullable=False)
    tweet_id = Column(Integer, nullable=True, unique=True)

    author = relationship(Users,
                          primaryjoin=author_id == Users.id,
                          foreign_keys='[PullRequests.author_id]',
                          backref='pull_requests'
                            )

    @property
    def diff_url(self):
        url = 'https://patch-diff.githubusercontent.com/raw/{0}/{1}/pull/{2}.diff'
        return url.format('bitcoin', 'bitcoin', self.number)

    @property
    def html_url(self):
        url = 'https://github.com/bitcoin/bitcoin/pull/{0}'
        return url.format(self.number)
