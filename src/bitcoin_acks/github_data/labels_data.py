from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.models import Labels
from bitcoin_acks.models.pull_requests_labels import PullRequestsLabels


class LabelsData(object):

    @staticmethod
    def delete(pull_request_id: str):
        with session_scope() as session:
            (
                session
                    .query(PullRequestsLabels)
                    .filter(PullRequestsLabels.pull_request_id == pull_request_id)
                    .delete()
            )

    @staticmethod
    def upsert(pull_request_id: str, data: dict):
        with session_scope() as session:
            try:
                record = (
                    session.query(Labels)
                        .filter(Labels.id == data['id'])
                        .one()
                )
            except NoResultFound:
                record = Labels()
                record.pull_request_id = pull_request_id
                session.add(record)

            for key, value in data.items():
                setattr(record, key, value)

            try:
                m2m_record = (
                    session.query(PullRequestsLabels)
                    .filter(
                        and_(
                            PullRequestsLabels.label_id == data['id'],
                            PullRequestsLabels.pull_request_id == pull_request_id
                        )
                    )
                    .one()
                )
            except NoResultFound:
                m2m_record = PullRequestsLabels()
                m2m_record.pull_request_id = pull_request_id
                m2m_record.label_id = data['id']
                session.add(m2m_record)
