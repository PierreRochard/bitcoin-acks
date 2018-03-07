import datetime

from sqlalchemy import Column, String, DateTime

from github_twitter.database.base import Base


class Responses(Base):
    __tablename__ = 'responses'

    etag = Column(String, primary_key=True)
    timestamp = Column(DateTime,
                       default=datetime.datetime.utcnow,
                       nullable=False)
