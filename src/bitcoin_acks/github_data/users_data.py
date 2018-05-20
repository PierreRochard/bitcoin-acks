from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.github_data import GitHubData
from bitcoin_acks.github_data.graphql_queries import user_graphql_query
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
                data = self.get(login=data['login'])
                user_record = Users()
                session.add(user_record)
            for key, value in data.items():
                setattr(user_record, key, value)
            session.commit()
            return user_record.id
