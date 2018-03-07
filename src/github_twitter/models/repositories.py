import datetime

import requests
from sqlalchemy import Column, String, DateTime, Integer

from github_twitter.database.base import Base
from github_twitter.database.session_scope import session_scope


class Repositories(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    name = Column(String)
    etag = Column(String)
    last_updated = Column(DateTime,
                          default=datetime.datetime.utcnow,
                          nullable=False)

    def get_events(self, page=1, per_page=300):
        with session_scope() as session:

            if not self.etag:
                headers = None
            else:
                headers = {'If-None-Match': self.etag}
            events_url = f'repos/{self.path}/{self.name}/events?page={page}&per_page={per_page}'
            response = requests.get(events_url, headers=headers)

            self.last_updated = datetime.datetime.utcnow()

            # 304 Not Modified due to etag
            if response.status_code == 304:
                return None

            self.etag = response.headers['etag']
