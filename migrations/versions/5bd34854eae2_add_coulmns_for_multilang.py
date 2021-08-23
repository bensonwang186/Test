"""Add coulmns for multilang

Revision ID: 5bd34854eae2
Revises: e4f52af076bc
Create Date: 2018-03-05 17:39:20.420081

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import TEXT


# revision identifiers, used by Alembic.
revision = '5bd34854eae2'
down_revision = 'e4f52af076bc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Configuration', sa.Column('langSetting', TEXT, nullable=True))


def downgrade():
    op.drop_column('Configuration', 'langSetting')
