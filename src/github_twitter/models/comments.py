from sqlalchemy import (
    Column,
    DateTime,
    String)
from sqlalchemy.orm import synonym

from github_twitter.database.base import Base


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(String, primary_key=True)

    body = Column(String)

    published_at = Column(DateTime, nullable=False)
    publishedAt = synonym('published_at')

    url = Column(String, nullable=False)

    pull_request_id = Column(String, nullable=False)
    author_id = Column(String)

    auto_detected_ack = Column(String)
    corrected_ack = Column(String)
