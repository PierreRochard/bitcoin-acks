from bitcoin_acks.constants import PullRequestState

pull_requests_get_all_test_cases = [
    (None, False, 105),
    (None, False, 0),
    (PullRequestState.OPEN, True, 20),
    (PullRequestState.MERGED, False, 220),
    (PullRequestState.CLOSED, True, 5)
]
