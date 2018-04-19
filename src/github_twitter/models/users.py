from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String
)

from github_twitter.database.base import Base


class Users(Base):
    __tablename__ = 'users'

    avatar_url = Column(String)
    events_url = Column(String)
    followers_url = Column(String)
    following_url = Column(String)
    gists_url = Column(String)
    gravatar_id = Column(String)
    html_url = Column(String)
    id = Column(Integer, primary_key=True)
    login = Column(String)
    organizations_url = Column(String)
    received_events_url = Column(String)
    repos_url = Column(String)
    site_admin = Column(Boolean)
    starred_url = Column(String)
    subscriptions_url = Column(String)
    type = Column(String)
    url = Column(String)

    twitter_handle = Column(String)
