"""add_coulmns_for_update_result

Revision ID: 24504294d512
Revises: 4bf43dbae32b
Create Date: 2021-07-05 10:10:21.541092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.dialects.sqlite import TEXT

revision = '24504294d512'
down_revision = '4bf43dbae32b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Configuration', sa.Column('updateResult', TEXT, nullable=True))


def downgrade():
    op.drop_column('Configuration', 'updateResult')
