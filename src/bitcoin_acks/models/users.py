from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy import (
    Boolean, Column,
    ForeignKey, Integer, PickleType, String, Table
)
from sqlalchemy.orm import relationship, synonym

from bitcoin_acks.database.base import Base
from bitcoin_acks.webapp.database import db


class Roles(Base, RoleMixin):
    __tablename__ = 'roles'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


# FIXME Change db.Model to Base for auto-gen migrations
class Users(db.Model, UserMixin):
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
    btcpay_pairing_code = Column(Integer)
    btcpay_client = Column(PickleType)



class OAuth(OAuthConsumerMixin, Base):
    __tablename__ = 'oauth'

    provider_user_id = Column(String(), unique=True, nullable=False)
    user_id = Column(String, ForeignKey(Users.id), nullable=False)
    user = relationship(Users)


roles_users = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
)
