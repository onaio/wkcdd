"""Added intial models

Revision ID: 2683594e0607
Revises: None
Create Date: 2014-03-17 15:56:30.182574

"""

# revision identifiers, used by Alembic.
revision = '2683594e0607'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('location_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('communities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('constituency_id', sa.Integer(), nullable=False),
    sa.Column('geolocation', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('project_code', sa.String(), autoincrement=False, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('community_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ),
    sa.PrimaryKeyConstraint('project_code')
    )
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.String(), nullable=False),
    sa.Column('report_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('report_data', postgresql.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('location_type', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['location_type'], ['location_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('projects')
    op.drop_table('locations')
    op.drop_table('reports')
    op.drop_table('communities')
    op.drop_table('location_types')
    ### end Alembic commands ###
