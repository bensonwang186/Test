"""security detection

Revision ID: b5c90e2f2126
Revises: 22ae3a0ca8f8
Create Date: 2020-03-23 18:23:36.975403

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME
from Utility import DataCryptor
from System.settings import PWD_KEY

# revision identifiers, used by Alembic.
revision = 'b5c90e2f2126'
down_revision = '22ae3a0ca8f8'
branch_labels = None
depends_on = None


def upgrade():
    cyptor = DataCryptor.Cryptor()
    key = cyptor.enc(PWD_KEY)
    op.add_column('Configuration', sa.Column('pwdKey', TEXT, nullable=False,server_default=sa.schema.DefaultClause(key)))


def downgrade():
    op.drop_column('Configuration', 'pwdKey')
