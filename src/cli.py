import sys
from datetime import timedelta, date

from bitcoin.core import COIN
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.constants import PullRequestState
from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.polling_data import PollingData
from bitcoin_acks.github_data.pull_requests_data import PullRequestsData
from bitcoin_acks.logging import log
from bitcoin_acks.models import PullRequests, Users
from bitcoin_acks.payments.recipient_btcpay import RecipientBTCPay
from bitcoin_acks.webapp.wsgi import app

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Interact with BitcoinACKs')
    parser.add_argument('-u',
                        dest='update_prs',
                        default=False)
    parser.add_argument('-p',
                        dest='pr_number',
                        type=int,
                        default=None)
    parser.add_argument('-s',
                        dest='state',
                        type=str,
                        choices=['OPEN', 'CLOSED', 'MERGED'],
                        default=None
                        )
    parser.add_argument('-l',
                        dest='limit',
                        type=int,
                        default=None
                        )
    parser.add_argument('-hp',
                        dest='high_priority',
                        type=bool,
                        default=False)
    parser.add_argument('-o',
                        dest='old',
                        type=bool,
                        default=False)

    args = parser.parse_args()

    if args.update_prs:
        pull_requests_data = PullRequestsData('bitcoin', 'bitcoin')
        polling_data = PollingData('github')

        if polling_data.is_polling():
            log.warn('GitHub is already being polled')
            sys.exit(0)

        polling_data.start()

        if args.pr_number is not None:
            pull_requests_data.update(number=args.pr_number)
        elif args.state is not None:
            args.state = PullRequestState[args.state]
            pull_requests_data.update_all(state=args.state,
                                          limit=args.limit)
        elif args.high_priority:
            with session_scope() as session:
                record = (
                    session
                        .query(PullRequests.number)
                        .filter(
                        and_(PullRequests.is_high_priority.isnot(None))
                    )
                        .all()
                )
                for r in record:
                    pull_requests_data.update(number=int(r.number))
        elif args.old:
            with session_scope() as session:
                try:
                    record = (
                        session
                        .query(PullRequests.updated_at)
                        .order_by(PullRequests.updated_at.desc())
                        .limit(1)
                        .one()
                    )
                    from_date = record.updated_at.date() - timedelta(days=1)
                except NoResultFound:
                    from_date = date(2000, 1, 1)
                pull_requests_data.update_all(newer_than=from_date,
                                              limit=args.limit)
        else:
            # All
            log.debug('All')
            pull_requests_data.update_all(limit=args.limit)

        polling_data.stop()
