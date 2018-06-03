from sqlalchemy import (
    Column,
    DateTime,
    String, Enum, func, ForeignKey)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym, relationship

from bitcoin_acks.constants import ReviewDecision
from bitcoin_acks.database.base import Base
from bitcoin_acks.models.users import Users


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(String, primary_key=True)

    body = Column(String)

    published_at = Column(DateTime, nullable=False)
    publishedAt = synonym('published_at')

    url = Column(String, nullable=False)

    pull_request_id = Column(String,
                             ForeignKey('pull_requests.id'),
                             nullable=False)
    author_id = Column(String)

    auto_detected_review_decision = Column(Enum(ReviewDecision))
    corrected_review_decision = Column(Enum(ReviewDecision))

    @hybrid_property
    def review_decision(self):
        return self.corrected_review_decision if self.corrected_review_decision else self.auto_detected_review_decision

    @review_decision.expression
    def review_decision(cls):
        return func.coalesce(cls.auto_detected_review_decision, cls.corrected_review_decision)

    author = relationship(Users,
                          primaryjoin=author_id == Users.id,
                          foreign_keys='[Comments.author_id]',
                          backref='comments'
                          )
