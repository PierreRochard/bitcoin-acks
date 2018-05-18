from bitcoin_acks.database.session import session_scope
from bitcoin_acks.database.base import Base

import bitcoin_acks.models


def create_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.create_all(session.connection())


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
    create_database()
