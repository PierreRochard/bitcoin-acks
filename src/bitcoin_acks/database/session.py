from contextlib import contextmanager
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

is_test = False


def get_url():
    db_name = (os.environ.get('GH_PGDATABASE', 'github')
               if not is_test else os.environ.get('TEST_GH_PGDATABASE', 'test_github'))

    pg_url = URL(drivername='postgresql+psycopg2',
                 username=os.environ['PGUSER'],
                 password=os.environ['PGPASSWORD'],
                 host=os.environ['PGHOST'],
                 port=os.environ['PGPORT'],
                 database=db_name)
    return pg_url


@contextmanager
def session_scope(echo=False,
                  raise_integrity_error=True,
                  raise_programming_error=True) -> Session:

    pg_url = get_url()
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
