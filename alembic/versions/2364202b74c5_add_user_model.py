"""Add user model

Revision ID: 2364202b74c5
Revises: 1d29df103cf6
Create Date: 2014-08-04 08:55:49.531745

"""

# revision identifiers, used by Alembic.
revision = '2364202b74c5'
down_revision = '1d29df103cf6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username',
                              sa.String(length=100),
                              nullable=False),
                    sa.Column('pwd', sa.String(length=255), nullable=True),
                    sa.Column('active',
                              sa.Boolean(),
                              server_default='false',
                              nullable=False),
                    sa.Column('group',
                              sa.String(length=10),
                              server_default='cpc',
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('username'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    ### end Alembic commands ###
