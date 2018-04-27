from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean)

from bitcoin_acks.database.base import Base
from bitcoin_acks.models.milestones import Milestones
from bitcoin_acks.models.users import Users
from bitcoin_acks.models.repositories import Repositories


class Issues(Base):
    __tablename__ = 'issues'

    active_lock_reason = Column(String)
    author_association = Column(String)
    body = Column(String)
    closed_at = Column(DateTime)
    comments = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    html_url = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    locked = Column(Boolean)
    milestone_id = Column(Integer, ForeignKey(Milestones.id))
    number = Column(Integer, nullable=False)
    repository_id = Column(Integer, ForeignKey(Repositories.id))
    state = Column(String)
    title = Column(String)
    updated_at = Column(DateTime)
    user_id = Column(String, ForeignKey(Users.id), nullable=False)
