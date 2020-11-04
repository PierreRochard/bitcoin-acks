from sqlalchemy import Table, Column, Integer, String, ForeignKey

from bitcoin_acks.database.base import Base

roles_users = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
)
