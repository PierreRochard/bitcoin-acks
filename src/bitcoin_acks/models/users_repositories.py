from sqlalchemy import Column, Integer, String, ForeignKey

from bitcoin_acks.database.base import Base


class UsersRepositories(Base):
    __tablename__ = 'users_repositories'
    id = Column(Integer, primary_key=True)
    repository_id = Column(String, ForeignKey('repositories.id'))
    user_id = Column(String, ForeignKey('users.id'))
