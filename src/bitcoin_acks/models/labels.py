from sqlalchemy import (
    Column,
    String
)

from bitcoin_acks.database.base import Base


class Labels(Base):
    __tablename__ = 'labels'

    id = Column(String, primary_key=True)
    name = Column(String)
    color = Column(String)
