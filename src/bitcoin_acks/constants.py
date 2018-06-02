from enum import Enum


class PullRequestState(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'


class ReviewDecision(Enum):
    NACK = 'NACK'
    CONCEPT_ACK = 'CONCEPT_ACK'
    UNTESTED_ACK = 'UNTESTED_ACK'
    TESTED_ACK = 'TESTED_ACK'
    NONE = None
