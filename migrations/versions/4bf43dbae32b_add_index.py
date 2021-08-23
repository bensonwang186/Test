"""'add_index'

Revision ID: 4bf43dbae32b
Revises: b5c90e2f2126
Create Date: 2020-09-01 14:28:44.902958

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '4bf43dbae32b'
down_revision = 'b5c90e2f2126'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('event_log_id_createTime_idx', 'EventLog', ['id', 'CreateTime'], unique=True)


def downgrade():
    op.drop_index('event_log_id_createTime_idx', table_name='EventLog')
