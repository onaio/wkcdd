"""Meeting reports

Revision ID: 309813cd859f
Revises: 4deb2bb4f2c2
Create Date: 2014-07-23 16:38:12.980246

"""

# revision identifiers, used by Alembic.
revision = '309813cd859f'
down_revision = '354891c319c5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'meeting_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.String(), nullable=False),
        sa.Column('period', sa.String(), nullable=False),
        sa.Column('submission_time',
                  sa.DateTime(timezone=True), nullable=False),
        sa.Column('report_data', postgresql.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('meeting_reports')
    ### end Alembic commands ###
