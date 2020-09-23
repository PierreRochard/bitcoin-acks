"""Add bounties model

Revision ID: 5ca8346d7f19
Revises: dcfdb05b9a0d
Create Date: 2020-07-09 02:31:29.390592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ca8346d7f19'
down_revision = 'dcfdb05b9a0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bounties',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('pull_request_id', sa.String(), nullable=False),
    sa.Column('creator_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bounties')
    # ### end Alembic commands ###