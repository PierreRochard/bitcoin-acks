from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from bitcoin_acks.database.base import Base
from bitcoin_acks.models import PullRequests
from bitcoin_acks.models.users import Users


class Bounties(Base):
    __tablename__ = 'bounties'

    id = Column(String, primary_key=True)

    amount = Column(Integer)

    published_at = Column(DateTime(timezone=True), nullable=False)

    pull_request_id = Column(String,
                             ForeignKey('pull_requests.id'),
                             nullable=False)

    pull_request = relationship(PullRequests, backref='bounties')

    creator_id = Column(String)

    creator = relationship(Users,
                           primaryjoin=creator_id == Users.id,
                           foreign_keys='[Bounties.creator_id]',
                           backref='bounties'
                           )
