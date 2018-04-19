from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database.base import Base
from github_twitter.database.session import session_scope
from github_twitter.models.users import Users


class Milestones(Base):
    __tablename__ = 'milestones'

    closed_at = Column(DateTime)
    closed_issues = Column(Integer)
    created_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey(Users.id))
    description = Column(String)
    due_on = Column(DateTime)
    html_url = Column(String)
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    open_issues = Column(Integer)
    state = Column(String)
    title = Column(String)
    updated_at = Column(DateTime)

    @staticmethod
    def insert_milestone(milestone: dict):
        with session_scope() as session:
            try:
                milestone_record = (
                    session.query(Milestones)
                        .filter(Milestones.id == milestone['id'])
                        .one()
                )
            except NoResultFound:
                milestone_record = Milestones()
                session.add(milestone_record)
            for key, value in milestone.items():
                if hasattr(milestone_record, key):
                    setattr(milestone_record, key, value)
            session.commit()
        return milestone['id']
