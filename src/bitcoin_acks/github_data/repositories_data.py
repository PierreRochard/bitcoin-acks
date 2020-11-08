from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.github_data import GitHubData
from bitcoin_acks.github_data.graphql_queries import repository_graphql_query
from bitcoin_acks.logging import log
from bitcoin_acks.models import Repositories, UsersRepositories


class RepositoriesData(GitHubData):
    def __init__(self, repository_path: str, repository_name: str):
        super(RepositoriesData, self).__init__()
        self.path = repository_path
        self.name = repository_name
        self.model, self.id = self.get_id()

    def get_id(self):
        with session_scope() as session:
            try:
                repository = (
                    session.query(Repositories)
                        .filter(
                        and_(
                            Repositories.path == self.path,
                            Repositories.name == self.name
                        )
                    )
                        .one()
                )
                return repository, repository.id
            except NoResultFound:
                repository_data = self.get()
                repository = Repositories()
                repository.id = repository_data['id']
                repository.path = self.path
                repository.name = self.name
                repository.created_at = repository_data['createdAt']
                repository.updated_at = repository_data['updatedAt']
                repository.description = repository_data['description']
                session.add(repository)
                session.flush()
                session.expunge(repository)
                return repository, repository_data['id']

    def get(self):
        json_object = {
            'query': repository_graphql_query,
            'variables': {'searchQuery': f'repo:{self.path}/{self.name}'}
        }
        log.debug('Variables for graphql repository query', json_object=json_object)

        data = self.graphql_post(json_object=json_object).json()

        search_data = data['data']['search']

        repositories_graphql_data = search_data['edges']
        results_count = len(repositories_graphql_data)

        log.debug(
            'response from github graphql',
            results_count=results_count
        )
        if results_count > 1:
            raise Exception('Multiple results found')
        elif results_count == 0:
            raise Exception('No GitHub repository found')

        repository_data = repositories_graphql_data[0]['node']
        return repository_data

    def associate_user(self, user_id):
        with session_scope() as session:
            try:
                relation = (
                    session.query(UsersRepositories)
                        .filter(
                        and_(
                            UsersRepositories.repository_id == self.id,
                            UsersRepositories.user_id == user_id
                        )
                    )
                        .one()
                )
            except NoResultFound:
                relation = UsersRepositories()
                relation.repository_id = self.id
                relation.user_id = user_id
                session.add(relation)

    def update(self):
        repository_data = self.get()
        with session_scope() as session:
            try:
                repository = (
                    session.query(Repositories)
                        .filter(
                        and_(
                            Repositories.path == self.path,
                            Repositories.name == self.name
                        )
                    )
                        .one()
                )
                repository.id = repository_data['id']
                repository.created_at = repository_data['createdAt']
                repository.updated_at = repository_data['updatedAt']
                repository.description = repository_data['description']
            except NoResultFound:
                repository = Repositories()
                repository.path = self.path
                repository.name = self.name
                repository.id = repository_data['id']
                repository.created_at = repository_data['createdAt']
                repository.updated_at = repository_data['updatedAt']
                repository.description = repository_data['description']
                session.add(repository)
