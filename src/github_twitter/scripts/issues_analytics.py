from sqlalchemy import func

from github_twitter.database.session_scope import session_scope
from github_twitter.models import Issues


class IssuesAnalytics(object):

    @staticmethod
    def monthly_created_count():
        with session_scope() as session:
            issues_stats = (
                session
                    .query(func.strftime('%Y-%m', Issues.created_at),
                           func.count(Issues.id),
                           func.round(func.avg(func.julianday(Issues.closed_at) - func.julianday(Issues.created_at)), 0))
                    .group_by(func.strftime('%Y-%m', Issues.created_at))
                    .filter(Issues.closed_at is not None)
                    .all()
            )
            for s in issues_stats:
                print(s)


def issues_analytics():
    with session_scope() as session:
        issues_stats = (
            session
                .query(func.strftime('%Y-%m', Issues.created_at),
                       func.count(Issues.id),
                       func.round(func.avg(func.julianday(Issues.closed_at) - func.julianday(Issues.created_at)), 0))
                .group_by(func.strftime('%Y-%m', Issues.created_at))
                .filter(Issues.closed_at is not None)
            .all()
        )
        for s in issues_stats:
            print(s)


if __name__ == '__main__':
    issues_analytics()
