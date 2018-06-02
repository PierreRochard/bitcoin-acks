from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    and_,
    select, func)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, synonym

from bitcoin_acks.constants import ReviewDecision
from bitcoin_acks.database.base import Base
from bitcoin_acks.models import Comments, Labels
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

    additions = Column(Integer)
    deletions = Column(Integer)

    mergeable = Column(String)
    last_commit_state = Column(String)
    last_commit_state_description = Column(String)
    last_commit_short_hash = Column(String)

    state = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    merged_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    comment_count = Column(Integer)
    # NB counts all of (nack, utack, tested ack, concept ack)
    ack_comment_count = Column(Integer)
    commit_count = Column(Integer)

    bodyHTML = synonym('body')
    createdAt = synonym('created_at')
    updatedAt = synonym('updated_at')
    mergedAt = synonym('merged_at')
    closedAt = synonym('closed_at')

    repository_id = Column(Integer, nullable=False)
    author_id = Column(String)
    tweet_id = Column(Integer, unique=True)

    author = relationship(Users,
                          primaryjoin=author_id == Users.id,
                          foreign_keys='[PullRequests.author_id]',
                          backref='pull_requests'
                          )

    review_decisions = relationship(Comments,
                                primaryjoin=and_(
                                    id == Comments.pull_request_id,
                                    Comments.ack != ReviewDecision.NONE,
                                    Comments.author_id != author_id
                                ),
                                foreign_keys='[Comments.pull_request_id]',
                                order_by=Comments.published_at.desc())

    @hybrid_property
    def review_decisions_count(self):
        return len(self.review_decisions)

    @review_decisions_count.expression
    def review_decisions_count(cls):
        return (select([func.count(Comments.id)])
                .where(and_(Comments.pull_request_id == cls.id,                                                   Comments.ack != ReviewDecision.NONE,
                            Comments.author_id != cls.author_id))
                .label('concept_acks_count')
                )

    concept_acks = relationship(Comments,
                                primaryjoin=and_(
                                    id == Comments.pull_request_id,
                                    Comments.ack == ReviewDecision.CONCEPT_ACK,
                                    Comments.author_id != author_id
                                ),
                                foreign_keys='[Comments.pull_request_id]',
                                order_by=Comments.published_at.desc())

    @hybrid_property
    def concept_acks_count(self):
        return len(self.concept_acks)

    @concept_acks_count.expression
    def concept_acks_count(cls):
        return (select([func.count(Comments.id)])
                .where(and_(Comments.pull_request_id == cls.id,
                            Comments.ack == ReviewDecision.CONCEPT_ACK,
                            Comments.author_id != cls.author_id))
                .label('concept_acks_count')
                )

    tested_acks = relationship(Comments,
                               primaryjoin=and_(
                                    id == Comments.pull_request_id,
                                    Comments.ack == ReviewDecision.TESTED_ACK,
                                    Comments.author_id != author_id
                               ),
                               foreign_keys='[Comments.pull_request_id]',
                               order_by=Comments.published_at.desc())

    @hybrid_property
    def tested_acks_count(self):
        return len(self.tested_acks)

    @tested_acks_count.expression
    def tested_acks_count(cls):
        return (select([func.count(Comments.id)])
                .where(and_(Comments.pull_request_id == cls.id,
                            Comments.ack == ReviewDecision.TESTED_ACK,
                            Comments.author_id != cls.author_id))
                .label('tested_acks_count')
                )

    untested_acks = relationship(Comments,
                               primaryjoin=and_(
                                   id == Comments.pull_request_id,
                                   Comments.ack == ReviewDecision.UNTESTED_ACK,
                                   Comments.author_id != author_id
                               ),
                               foreign_keys='[Comments.pull_request_id]',
                               order_by=Comments.published_at.desc())

    @hybrid_property
    def untested_acks_count(self):
        return len(self.untested_acks)

    @untested_acks_count.expression
    def untested_acks_count(cls):
        return (select([func.count(Comments.id)])
                .where(and_(Comments.pull_request_id == cls.id,
                            Comments.ack == ReviewDecision.UNTESTED_ACK,
                            Comments.author_id != cls.author_id))
                .label('untested_acks_count')
                )

    nacks = relationship(Comments,
                                 primaryjoin=and_(
                                     id == Comments.pull_request_id,
                                     Comments.ack == ReviewDecision.NACK,
                                     Comments.author_id != author_id
                                 ),
                                 foreign_keys='[Comments.pull_request_id]',
                                 order_by=Comments.published_at.desc())

    @hybrid_property
    def nacks_count(self):
        return len(self.nacks)

    @nacks_count.expression
    def nacks_count(cls):
        return (select([func.count(Comments.id)])
                .where(and_(Comments.pull_request_id == cls.id,
                            Comments.ack == ReviewDecision.NACK,
                            Comments.author_id != cls.author_id))
                .label('nacks_count')
                )

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
