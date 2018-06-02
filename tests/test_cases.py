from bitcoin_acks.constants import PullRequestState

pull_requests_get_all_test_cases = [
    (None, 105),
    (None, 0),
    (PullRequestState.OPEN, 20),
    (PullRequestState.MERGED, 220),
    (PullRequestState.CLOSED, 5)
]
