from sqlalchemy import (
    Column,
    DateTime,
    func,
    Integer,
    String
)

from github_twitter.database.base import Base


class Diffs(Base):
    __tablename__ = 'diffs'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    id = Column(Integer, primary_key=True)
    pull_request_id = Column(Integer)
    diff_hash = Column(String, unique=True)

    diff = Column(String)
    added_lines = Column(Integer)
    removed_lines = Column(Integer)
    added_files = Column(Integer)
    modified_files = Column(Integer)
    removed_files = Column(Integer)
