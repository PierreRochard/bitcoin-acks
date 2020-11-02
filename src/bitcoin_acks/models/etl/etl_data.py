from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from bitcoin_acks.database.base import Base


class ETLData(Base):
    __tablename__ = 'etl_data'

    id = Column(Integer, primary_key=True)
    data = Column(JSONB)
