import hashlib

import requests
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from unidiff import PatchSet

from bitcoin_acks.database import session_scope
from bitcoin_acks.models.diffs import Diffs


class DiffsData(object):

    @classmethod
    def get(cls,
            repository_path: str,
            repository_name: str,
            pull_request_number: int) -> str:
        url = 'https://patch-diff.githubusercontent.com/raw/{0}/{1}/pull/{2}.diff'
        url = url.format(repository_path, repository_name, pull_request_number)
        diff = requests.get(url).text
        return diff

    @classmethod
    def insert(cls, pull_request_id: str, associated_commit_hash: str,
               diff: str):
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
                record.associated_commit_hash = associated_commit_hash
                session.add(record)

            (
                session.query(Diffs)
                    .filter(
                    and_(
                        Diffs.diff_hash != diff_hash,
                        Diffs.pull_request_id == pull_request_id
                    )
                ).update({Diffs.is_most_recent: False})
            )
