from flask_login import current_user
from sqlalchemy import func

from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.models import UsersRepositories, Repositories
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class RepositoriesModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(RepositoriesModelView, self).__init__(model, session, *args, **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'repositories'
        self.name = 'Repositories'

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .join(UsersRepositories, self.model.users_repositories)
                .filter(UsersRepositories.user_id == current_user.id)
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .join(UsersRepositories, self.model.users_repositories)
                .filter(UsersRepositories.user_id == current_user.id)
        )

    def create_model(self, form):
        repo = RepositoriesData(repository_path=form.data['path'], repository_name=form.data['name'])
        repo.associate_user(current_user.id)
        return repo.model

    form_excluded_columns = ['users_repositories', 'created_at', 'updated_at', 'description']
    column_display_actions = False
    can_create = True
