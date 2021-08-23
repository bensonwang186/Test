"""add_coulmns_for_cloud_account

Revision ID: 2d01b482d0a3
Revises: 24504294d512
Create Date: 2021-07-06 18:12:52.824107

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import BOOLEAN, TEXT

# revision identifiers, used by Alembic.
revision = '2d01b482d0a3'
down_revision = '24504294d512'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Configuration', sa.Column('agree_policy', BOOLEAN, nullable=True))

def downgrade():
    op.drop_column('Configuration', 'agree_policy')
