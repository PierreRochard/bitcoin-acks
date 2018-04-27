from sqlalchemy import (
    Column,
    String
)
from sqlalchemy.orm import synonym

from bitcoin_acks.database.base import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    login = Column(String, unique=True)

    name = Column(String)
    bio = Column(String)
    url = Column(String)

    avatar_url = Column(String)
    avatarUrl = synonym('avatar_url')

    twitter_handle = Column(String)
