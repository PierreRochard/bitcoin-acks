#! /usr/bin/env zsh

service cron start

# Let the DB start
sleep 10;
# Run migrations
cd /app && alembic --config src/bitcoin_acks/migrations/alembic.ini upgrade head
