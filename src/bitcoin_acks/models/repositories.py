from sqlalchemy import Column, Integer, String

from bitcoin_acks.database.base import Base


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(String, primary_key=True)
    path = Column(String)
    name = Column(String)
