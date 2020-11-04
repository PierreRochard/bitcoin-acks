from sqlalchemy import Column, Integer, String

from bitcoin_acks.database.base import Base


class UsersRepositories(Base):
    __tablename__ = 'users_repositories'
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer)
    user_id = Column(String)
