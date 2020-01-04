import os

from alembic import command, script
from alembic.config import Config
from alembic.runtime import migration
from sqlalchemy import engine

from bitcoin_acks.database.session import session_scope
from bitcoin_acks.database.base import Base

import bitcoin_acks.models


def get_current_head(connectable: engine.Engine) -> set:
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        current_head = set(context.get_current_heads())
        return current_head


def create_or_update_database(echo=True):
    file_path = os.path.realpath(__file__)
    app_path = os.path.dirname(os.path.dirname(file_path))
    config_path = os.path.join(app_path, 'migrations', 'alembic.ini')

    alembic_config = Config(config_path)

    with session_scope(echo=echo) as session:
        directory = script.ScriptDirectory.from_config(alembic_config)
        get_head = set(directory.get_heads())
        current_head = get_current_head(connectable=session.bind.engine)
        if current_head == get_head:
            return
        elif not current_head:
            Base.metadata.create_all(session.connection())
            command.stamp(alembic_config, 'head')
        else:
            command.upgrade(alembic_config, 'head')


def drop_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.drop_all(session.connection())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Change the schema')

    parser.add_argument('-d',
                        dest='drop',
                        type=bool,
                        default=False
                        )
    args = parser.parse_args()
    if args.drop:
        drop_database()
    create_or_update_database()
