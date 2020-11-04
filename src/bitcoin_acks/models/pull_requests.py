from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    and_
)
from sqlalchemy.orm import relationship, synonym

from bitcoin_acks.constants import ReviewDecision
from bitcoin_acks.database.base import Base
from bitcoin_acks.models.comments import Comments
from bitcoin_acks.models.labels import Labels
from bitcoin_acks.models.pull_requests_labels import PullRequestsLabels
from bitcoin_acks.models.users import Users


class PullRequests(Base):
    __tablename__ = 'pull_requests'
    __table_args__ = (UniqueConstraint('number',
                                       'repository_id',
                                       name='pull_requests_unique_constraint'),
                      )

    id = Column(String, primary_key=True)
    number = Column(Numeric, nullable=False)

    is_high_priority = Column(DateTime)

    added_to_high_priority = Column(DateTime)
    removed_from_high_priority = Column(DateTime)

    additions = Column(Integer)
    deletions = Column(Integer)

    mergeable = Column(String)
    last_commit_state = Column(String)
    last_commit_state_description = Column(String)
    last_commit_short_hash = Column(String)
    last_commit_pushed_date = Column(DateTime(timezone=True))

    state = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    merged_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    commit_count = Column(Integer)
    review_decisions_count = Column(Integer, default=0)

    total_bounty_amount = Column(Integer)

    bodyHTML = synonym('body')
    createdAt = synonym('created_at')
    updatedAt = synonym('updated_at')
    mergedAt = synonym('merged_at')
    closedAt = synonym('closed_at')

    repository_id = Column(Integer, nullable=False)
    author_id = Column(String)
    tweet_id = Column(Integer, unique=True)
    toot_id = Column(Integer, unique=True)

    author = relationship(Users,
                          primaryjoin=author_id == Users.id,
                          foreign_keys='[PullRequests.author_id]',
                          backref='pull_requests'
                          )

    review_decisions = relationship(Comments,
                                    primaryjoin=and_(
                                        id == Comments.pull_request_id,
                                        Comments.review_decision != ReviewDecision.NONE,
                                        Comments.author_id != author_id
                                    ),
                                    foreign_keys='[Comments.pull_request_id]',
                                    order_by=Comments.published_at.desc())

    labels = relationship(Labels,
                          secondary=PullRequestsLabels.__table__,
                          primaryjoin=id == PullRequestsLabels.pull_request_id,
                          secondaryjoin=PullRequestsLabels.label_id == Labels.id,
                          # foreign_keys='[Labels.pull_request_id]',
                          backref='pull_request',
                          order_by=Labels.name)

    @property
    def html_url(self):
        url = 'https://github.com/bitcoin/bitcoin/pull/{0}'
        return url.format(self.number)

    def __repr__(self):
        return f'{self.number} {self.title}'
