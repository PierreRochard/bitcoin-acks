from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.models.polling import ServicePolling


class PollingData(object):
    def __init__(self, service: str):
        self.service = service

    def is_polling(self) -> bool:
        with session_scope() as session:
            try:
                record = (
                    session.query(ServicePolling)
                        .filter(ServicePolling.service == self.service)
                        .filter(ServicePolling.stopped_at.is_(None))
                        .one()
                )
                return True
            except NoResultFound:
                return False

    def start(self):
        new_record = ServicePolling(service=self.service,
                                    started_at=datetime.utcnow())
        with session_scope() as session:
            session.add(new_record)

    def stop(self):
        with session_scope() as session:
            try:
                record = (
                    session.query(ServicePolling)
                        .filter(ServicePolling.service == self.service)
                        .filter(ServicePolling.stopped_at.is_(None))
                        .one()
                )
                record.stopped_at = datetime.utcnow()
            except NoResultFound:
                pass


if __name__ == '__main__':
    PollingData('github').stop()
