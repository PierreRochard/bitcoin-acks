from contextlib import contextmanager
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import sessionmaker, Session

from bitcoin_acks.logging import log

load_dotenv()

is_test = False


def get_url():
    pg_url = URL(drivername='postgresql+psycopg2',
                 username=os.environ['POSTGRES_USER'],
                 password=os.environ['POSTGRES_PASSWORD'],
                 host=os.environ['PGHOST'],
                 port=os.environ['PGPORT'],
                 database=os.environ['POSTGRES_DB'])
    log.debug('get PG url', pg_url=pg_url)
    return pg_url


pg_url = get_url()


@contextmanager
def session_scope(echo=False,
                  raise_integrity_error=True,
                  raise_programming_error=True) -> Session:
    engine = create_engine(pg_url, echo=echo,
                           connect_args={'sslmode': 'prefer'})
    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    try:
        yield session
        session.commit()
    except IntegrityError:
        session.rollback()
        if raise_integrity_error:
            raise
    except ProgrammingError:
        session.rollback()
        if raise_programming_error:
            raise
    except:
        session.rollback()
        raise
    finally:
        session.close()
