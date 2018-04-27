from sqlalchemy import (
    Column,
    DateTime,
    String)
from sqlalchemy.orm import synonym, relationship

from bitcoin_acks.database.base import Base
from bitcoin_acks.models.users import Users


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

    author = relationship(Users,
                          primaryjoin=author_id == Users.id,
                          foreign_keys='[Comments.author_id]',
                          backref='comments'
                          )
