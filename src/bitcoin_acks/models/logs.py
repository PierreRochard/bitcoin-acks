from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy.sql import func

from bitcoin_acks.database.base import Base


class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())

    path = Column(String)
    full_path = Column(String)
    method = Column(String)
    ip = Column(String)
    user_agent = Column(String)
    status = Column(Integer)
