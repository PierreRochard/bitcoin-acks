from sqlalchemy import (
    Column,
    DateTime,
    Integer, String,
)

from bitcoin_acks.database.base import Base


class ServicePolling(Base):
    __tablename__ = 'service_polling'

    id = Column(Integer, primary_key=True)
    service = Column(String)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)
