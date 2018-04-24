from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String)

from github_twitter.database.base import Base


class Comments(Base):
    __tablename__ = 'comments'

    body = Column(String)
    published_at = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    pull_request_id = Column(String, nullable=False)
    author_id = Column(String, nullable=False)

    auto_detected_ack = Column(String)
    corrected_ack = Column(String)
