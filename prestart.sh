#! /usr/bin/env zsh
echo "prestart.sh script beginning"
echo "Starting cron service"
service cron start

echo "Sleeping for 10 seconds to let the DB start"

sleep 10;
echo "Creating database or running migrations"
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/database/createdb.py

echo "Clearing out any polling locks"
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/github_data/polling_data.py
echo "Doing a first update of the database"
cd /app && /usr/local/bin/python3.8 src/bitcoin_acks/github_data/pull_requests_data.py -l 5

flask run --host=0.0.0.0