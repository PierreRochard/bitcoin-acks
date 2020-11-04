from flask_security import RoleMixin
from sqlalchemy import (
    Column,
    Integer, String
)

from bitcoin_acks.database.base import Base


class Roles(Base, RoleMixin):
    __tablename__ = 'roles'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
