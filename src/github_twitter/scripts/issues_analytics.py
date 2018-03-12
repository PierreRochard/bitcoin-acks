from sqlalchemy import func

from github_twitter.database.session_scope import session_scope
from github_twitter.models import Issues


def issues_analytics():
    with session_scope() as session:
        issues_stats = (
            session
                .query(func.strftime('%Y-%m', Issues.created_at),
                       func.count(Issues.id))
                .group_by(func.strftime('%Y-%m', Issues.created_at))
            .all()
        )
        for s in issues_stats:
            print(s)


if __name__ == '__main__':
    issues_analytics()
