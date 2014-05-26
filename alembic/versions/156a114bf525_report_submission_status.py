"""Report submission status

Revision ID: 156a114bf525
Revises: 495e5d2a3c9a
Create Date: 2014-05-20 12:18:47.409619

"""

# revision identifiers, used by Alembic.
revision = '156a114bf525'
down_revision = '495e5d2a3c9a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


def upgrade():
    # commands auto generated by Alembic - please adjust! ###
    ENUM(
        'pending',
        'approved',
        'rejected',
        name="SUBMISSION_STATUS"
    ).create(
        op.get_bind(), checkfirst=False)
    op.add_column('reports',
                  sa.Column('status', sa.Enum(name='SUBMISSION_STATUS'),
                            nullable=False, server_default='pending'))

    op.create_index(op.f('ix_reports_status'),
                    'reports', ['status'], unique=False)

    op.execute(
        'update reports set status = {}'.format(
            op.inline_literal('approved')))
    # end Alembic commands ###


def downgrade():
    # commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_reports_status'), table_name='reports')
    op.drop_column('reports', 'status')
    ENUM(name="SUBMISSION_STATUS").drop(op.get_bind(), checkfirst=False)
    # end Alembic commands ###
