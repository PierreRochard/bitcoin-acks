from sqlalchemy import Column, Integer, String

from bitcoin_acks.database.base import Base


class PullRequestsLabels(Base):
    __tablename__ = 'pull_requests_labels'
    id = Column(Integer, primary_key=True)
    pull_request_id = Column(String)
    label_id = Column(String)
