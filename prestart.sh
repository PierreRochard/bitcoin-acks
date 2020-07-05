#! /usr/bin/env zsh

service cron start

# Let the DB start
sleep 10;
# Run migrations
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/database/createdb.py

# Clear out any polling locks
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/github_data/polling_data.py
# Do a first update of the database
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/github_data/pull_requests_data.py -l 5
