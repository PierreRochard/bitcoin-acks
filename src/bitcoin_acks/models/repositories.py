from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from bitcoin_acks.database.base import Base
from bitcoin_acks.models.users_repositories import UsersRepositories


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(String, primary_key=True)
    path = Column(String)
    name = Column(String)
    description = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    users_repositories = relationship(
        UsersRepositories,
        primaryjoin=id == UsersRepositories.repository_id,
        foreign_keys='[UsersRepositories.repository_id]',
        backref='repositories'
    )
