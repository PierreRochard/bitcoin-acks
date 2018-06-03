### Creating a migration
alembic --config src/bitcoin_acks/migrations/alembic.ini revision --autogenerate -m "Revision description"


### Migrating
alembic --config src/bitcoin_acks/migrations/alembic.ini upgrade head