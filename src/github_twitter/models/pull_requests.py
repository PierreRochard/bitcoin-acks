from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, synonym

from github_twitter.database.base import Base
from github_twitter.models.users import Users


class PullRequests(Base):
    __tablename__ = 'pull_requests'
    __table_args__ = (UniqueConstraint('number',
                                       'repository_id',
                                       name='pull_requests_unique_constraint'),
                      )

    id = Column(String, primary_key=True)
    number = Column(Numeric, nullable=False)

    additions = Column(Integer)
    deletions = Column(Integer)

    state = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime)
    closed_at = Column(DateTime)

    comments_count = Column(Integer)

    createdAt = synonym('created_at')
    updatedAt = synonym('updated_at')
    mergedAt = synonym('merged_at')
    closedAt = synonym('closed_at')

    repository_id = Column(Integer, nullable=False)
    author_id = Column(String, nullable=False)
    tweet_id = Column(Integer, unique=True)

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
