from sqlalchemy import (
    Column,
    DateTime,
    Integer,
)

from bitcoin_acks.database.base import Base


class Polling(Base):
    __tablename__ = 'polling'

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer)
    last_event = Column(DateTime)
    last_open_update = Column(DateTime)
    last_full_update = Column(DateTime)
