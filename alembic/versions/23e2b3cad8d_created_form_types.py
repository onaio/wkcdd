"""created form types

Revision ID: 23e2b3cad8d
Revises: 193b377a3ffc
Create Date: 2014-03-18 19:22:07.994938

"""

# revision identifiers, used by Alembic.
revision = '23e2b3cad8d'
down_revision = '193b377a3ffc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('form_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'forms', sa.Column('form_type_id', sa.Integer(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'forms', 'form_type_id')
    op.drop_table('form_types')
    ### end Alembic commands ###
