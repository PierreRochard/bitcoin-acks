#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/ubuntu/github-twitter/src/')
print('\n'.join(sys.path))
from github_twitter.scripts.get_pull_requests import get_pull_requests
from github_twitter.scripts.send_tweet import send_tweet

if __name__ == '__main__':
    get_pull_requests()
    send_tweet()
