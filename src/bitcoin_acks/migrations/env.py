from __future__ import with_statement
from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import create_engine

file_path = os.path.realpath(__file__)
src_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
# parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(src_path)
print(src_path)

from bitcoin_acks.database.base import Base
from bitcoin_acks.database.session import get_url


config = context.config

fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline():
    url = get_url()
    context.configure(url=url,
                      target_metadata=target_metadata,
                      literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(get_url())

    with engine.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
