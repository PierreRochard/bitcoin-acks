from enum import Enum


class PullRequestState(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'
