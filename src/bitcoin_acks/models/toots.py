import datetime

from sqlalchemy import Column, DateTime, Integer

from bitcoin_acks.database.base import Base


class Toots(Base):
    __tablename__ = 'toots'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False,
                       default=datetime.datetime.utcnow, )
    pull_request_id = Column(Integer, nullable=False, unique=True)
