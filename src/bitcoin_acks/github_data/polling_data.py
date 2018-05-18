from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.models.polling import Polling


class PollingData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(PollingData, self).__init__(repository_path=repository_path,
                                          repository_name=repository_name)

    def update(self, last_event: bool = False, last_open_update: bool = False,
               last_full_update: bool = False):
        with session_scope() as session:
            try:
                record = (
                    session.query(Polling)
                        .filter(Polling.repository_id == self.repo.id)
                        .one()
                )
            except NoResultFound:
                record = Polling()
                record.repository_id = self.repo.id
                session.add(record)

            if last_event:
                record.last_event = datetime.utcnow()

            if last_open_update:
                record.last_open_update = datetime.utcnow()

            if last_full_update:
                record.last_full_update = datetime.utcnow()
