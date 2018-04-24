import re
from sqlalchemy.orm.exc import NoResultFound

from github_twitter.database import session_scope
from github_twitter.github_data.github_data import GitHubData
from github_twitter.models import Users


class UsersData(GitHubData):

    def get(self, login: str) -> dict:
        with open('user.graphql', 'r') as query_file:
            query = query_file.read()

        variables = {
            'userLogin': login
        }
        json_object = {
            'query': query,
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
                # key_parts = re.findall('[A-Z][^A-Z]*', key)
                key_parts = [a.lower() for a in re.split(r'([A-Z][a-z]*)', key) if a]
                modified_key = '_'.join(key_parts)
                setattr(user_record, modified_key, value)
            session.commit()
            return user_record.id
