from sqlalchemy import Column, Integer, String

from github_twitter.database.base import Base


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    name = Column(String)
