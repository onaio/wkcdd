"""Saic meetings report

Revision ID: 1d29df103cf6
Revises: 309813cd859f
Create Date: 2014-07-28 09:43:26.846234

"""

# revision identifiers, used by Alembic.
revision = '1d29df103cf6'
down_revision = '309813cd859f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('meeting_reports', sa.Column(
        'report_form_id',
        sa.String(),
        nullable=False,
        default='meeting_report'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('meeting_reports', 'report_form_id')
    ### end Alembic commands ###
