from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.github_data import GitHubData
from bitcoin_acks.github_data.users_data import UsersData
from bitcoin_acks.models import Comments


class CommentsData(GitHubData):

    @staticmethod
    def identify_ack(text: str):
        text = text.lower()
        if 'concept ack' in text:
            return 'Concept ACK'
        elif 'tested ack' in text:
            return 'Tested ACK'
        elif 'utack' in text:
            return 'utACK'
        elif 'nack' in text:
            return 'NACK'
        else:
            return None

    def upsert(self, pull_request_id: str, data: dict)  -> bool:
        ack = self.identify_ack(data['body'])
        if ack is None:
            return False

        with session_scope() as session:
            try:
                record = (
                    session.query(Comments)
                        .filter(Comments.id == data['id'])
                        .one()
                )
            except NoResultFound:
                record = Comments()
                record.pull_request_id = pull_request_id
                session.add(record)

            author = data.pop('author')
            if author is not None:
                record.author_id = UsersData().upsert(data=author)

            for key, value in data.items():
                setattr(record, key, value)
            record.auto_detected_ack = self.identify_ack(record.body)
        return True
