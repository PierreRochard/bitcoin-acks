from contextlib import contextmanager
import os

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import sessionmaker, Session


@contextmanager
def session_scope(echo: bool = False,
                  raise_integrity_error: bool = True,
                  raise_programming_error: bool = True) -> Session:
    file_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(file_path, 'github_twitter.db')
    url = URL(drivername='sqlite',
              database=db_path)

    engine = create_engine(url, echo=echo)
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
