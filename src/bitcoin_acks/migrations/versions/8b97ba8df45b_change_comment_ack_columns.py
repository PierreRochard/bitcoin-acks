"""change comment ack columns

Revision ID: 8b97ba8df45b
Revises: 154063888264
Create Date: 2018-06-03 12:39:11.037210

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8b97ba8df45b'
down_revision = '154063888264'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('auto_detected_review_decision',
                                        sa.Enum('NACK', 'CONCEPT_ACK',
                                                'UNTESTED_ACK', 'TESTED_ACK',
                                                'NONE', name='reviewdecision'),
                                        nullable=True))
    op.add_column('comments', sa.Column('corrected_review_decision',
                                        sa.Enum('NACK', 'CONCEPT_ACK',
                                                'UNTESTED_ACK', 'TESTED_ACK',
                                                'NONE', name='reviewdecision'),
                                        nullable=True))

    op.drop_column('comments', 'auto_detected_ack')
    op.drop_column('comments', 'corrected_ack')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments',
                  sa.Column('corrected_ack', sa.VARCHAR(), autoincrement=False,
                            nullable=True))
    op.add_column('comments', sa.Column('auto_detected_ack', sa.VARCHAR(),
                                        autoincrement=False, nullable=True))
    op.drop_column('comments', 'corrected_review_decision')
    op.drop_column('comments', 'auto_detected_review_decision')
    # ### end Alembic commands ###