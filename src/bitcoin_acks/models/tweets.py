import datetime

from sqlalchemy import BIGINT, Column, DateTime

from bitcoin_acks.database.base import Base


class Tweets(Base):
    __tablename__ = 'tweets'

    id = Column(BIGINT, primary_key=True)
    timestamp = Column(DateTime, nullable=False,
                       default=datetime.datetime.utcnow, )
    pull_request_id = Column(BIGINT, nullable=False, unique=True)
