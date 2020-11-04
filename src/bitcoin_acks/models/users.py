from flask_login import UserMixin
from sqlalchemy import (
    Boolean, Column,
    PickleType, String
)
from sqlalchemy.orm import synonym

from bitcoin_acks.database.base import Base
from bitcoin_acks.webapp.database import db


# FIXME Change db.Model to Base for auto-gen migrations
class Users(Base, db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    login = Column(String, unique=True)

    name = Column(String)
    bio = Column(String)
    url = Column(String)

    email = Column(String, unique=True)
    is_active = Column(Boolean)

    avatar_url = Column(String)
    avatarUrl = synonym('avatar_url')

    twitter_handle = Column(String)

    btcpay_host = Column(String)
    btcpay_pairing_code = Column(String)
    btcpay_client = Column(PickleType)

    @property
    def best_name(self):
        return self.name or self.login
