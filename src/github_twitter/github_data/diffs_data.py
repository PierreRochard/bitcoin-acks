import hashlib

from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from unidiff import PatchSet

from github_twitter.database import session_scope
from github_twitter.models.diffs import Diffs


class DiffsData(object):

    @classmethod
    def insert(cls, pull_request_id: int, diff: str):
        bdiff = diff.encode('utf-8')
        diff_hash = hashlib.sha256(bdiff).hexdigest()
        with session_scope() as session:
            try:
                (
                    session.query(Diffs)
                        .filter(
                        and_(
                            Diffs.pull_request_id == pull_request_id,
                            Diffs.diff_hash == diff_hash
                        )
                    )
                        .one()
                )
            except NoResultFound:
                record = Diffs()
                record.pull_request_id = pull_request_id
                record.diff_hash = diff_hash
                record.diff = diff
                patch = PatchSet(diff)
                record.added_lines = patch.added
                record.removed_lines = patch.removed
                record.added_files = len(patch.added_files)
                record.modified_files = len(patch.modified_files)
                record.removed_files = len(patch.removed_files)
                session.add(record)

            (
                session.query(Diffs).update({Diffs.is_most_recent: False})
                    .filter(
                    and_(
                        Diffs.diff_hash != diff_hash,
                        Diffs.pull_request_id == pull_request_id
                    )
                )
            )
