import traceback
from datetime import timedelta, date, datetime
from tempfile import TemporaryDirectory

from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.polling_data import PollingData
from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from bitcoin_acks.logging import log
from bitcoin_acks.models import PullRequests
from bitcoin_acks.scripts.send_email import email

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Interact with BitcoinACKs')
    parser.add_argument(
        '-u',
        dest='update_prs',
        action='store_true',
        default=False
    )
    parser.add_argument(
        '-s',
        dest='state',
        type=str,
        choices=['OPEN', 'CLOSED', 'MERGED'],
        default=None
    )
    parser.add_argument(
        '-l',
        dest='limit',
        type=int,
        default=None
    )
    parser.add_argument(
        '-o',
        dest='old',
        default=False,
        action='store_true'
    )

    args = parser.parse_args()
    log.debug('CLI', args=args)

    if args.update_prs:
        try:
            with TemporaryDirectory() as temporary_directory_path:
                pull_requests_data = PullRequestsData('bitcoin', 'bitcoin', temporary_directory_path)
                polling_data = PollingData('github')
            if polling_data.is_polling():
                raise Exception('GitHub is already being polled')

            polling_data.start()
            if args.old:
                from_date = date(2000, 1, 1)
            else:
                with session_scope() as session:
                    try:
                        record = (
                            session
                                .query(PullRequests.updated_at)
                                .order_by(PullRequests.updated_at.desc())
                                .limit(1)
                                .one()
                        )
                        from_date = record.updated_at
                    except NoResultFound:
                        from_date = datetime(2009, 1, 1)
            log.debug('Updating PRs starting from', from_date=from_date)
            if args.state is not None:
                args.state = PullRequestState[args.state]
                pull_requests_data.update_all(newer_than=from_date, state=args.state, limit=args.limit)
            else:
                pull_requests_data.update_all(newer_than=from_date, limit=args.limit)
        except Exception as e:
            log.error('polling exception', exc_info=e)
            tb = traceback.format_exc()
            email.notify('Polling exception\n\n' + tb)
        else:
            tb = "No error"
        finally:
            polling_data.stop()
