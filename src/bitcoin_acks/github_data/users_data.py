from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.github_data import GitHubData
from bitcoin_acks.github_data.graphql_queries import user_graphql_query
from bitcoin_acks.logging import log
from bitcoin_acks.models import Users


class UsersData(GitHubData):

    def get(self, login: str) -> dict:
        variables = {
            'userLogin': login
        }
        json_object = {
            'query': user_graphql_query,
            'variables': variables
        }
        log.debug('getting user', json_object=json_object)
        r = self.graphql_post(json_object=json_object)
        user = r.json()['data']['user']
        return user

    def upsert(self, data: dict) -> str:
        with session_scope() as session:
            try:
                user_record = (
                    session.query(Users)
                        .filter(Users.login == data['login'])
                        .one()
                )
            except NoResultFound:
                # if the login is not in the db, query github to get the ID
                data = self.get(login=data['login'])
                try:
                    user_record = (
                        session.query(Users)
                            .filter(Users.id == data['id'])
                            .one()
                    )
                except NoResultFound:
                    user_record = Users()
                    user_record.id = data['id']
                    session.add(user_record)

            for key, value in data.items():
                setattr(user_record, key, value)
            session.commit()

            return user_record.id
