from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy import (
    Column,
    ForeignKey, String
)
from sqlalchemy.orm import relationship

from bitcoin_acks.database.base import Base
from bitcoin_acks.models.users import Users


class OAuth(OAuthConsumerMixin, Base):
    __tablename__ = 'oauth'

    provider_user_id = Column(String(), unique=True, nullable=False)
    user_id = Column(String, ForeignKey(Users.id), nullable=False)
    user = relationship(Users)
