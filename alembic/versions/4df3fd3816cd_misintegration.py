"""misintegration

Revision ID: 4df3fd3816cd
Revises: 354891c319c5
Create Date: 2014-07-11 16:10:37.351850

"""

# revision identifiers, used by Alembic.
revision = '4df3fd3816cd'
down_revision = '354891c319c5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('locations', sa.Column('mis_code', sa.Text(), nullable=True))
    op.create_index(
        op.f('ix_locations_location_type'),
        'locations',
        ['location_type'],
        unique=False)
    op.drop_index('ix_location_type', table_name='locations')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        'ix_location_type',
        'locations',
        ['location_type'],
        unique=False)
    op.drop_index(
        op.f('ix_locations_location_type'), table_name='locations')
    op.drop_column('locations', 'mis_code')
    ### end Alembic commands ###