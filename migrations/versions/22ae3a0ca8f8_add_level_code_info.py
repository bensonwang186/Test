"""add level code info

Revision ID: 22ae3a0ca8f8
Revises: 2757838dc2c1
Create Date: 2020-03-19 17:43:12.069542

"""
import sys
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME

# revision identifiers, used by Alembic.
revision = '22ae3a0ca8f8'
down_revision = '2757838dc2c1'
branch_labels = None
depends_on = None


def upgrade():
    hardwareFaultLevelInfo = op.create_table('HardwareFaultLevelInfo',
                    sa.Column('Id', INTEGER, autoincrement=True, primary_key=True),
                    sa.Column('Level', INTEGER, nullable=False),
                    sa.Column('LevelCode', TEXT, nullable=False),
                    sa.Column('ColorCode', TEXT, nullable=False),
                    sa.Column('Note', TEXT)
                    )

    op.bulk_insert(hardwareFaultLevelInfo,
       [
           {'Level': 0, 'LevelCode': '0', 'ColorCode': '#777777', 'IsActive': '1'},
           {'Level': 1, 'LevelCode': '1', 'ColorCode': '#fdc503', 'IsActive': '1'},
           {'Level': 2, 'LevelCode': '2', 'ColorCode': '#fdc503', 'IsActive': '1'},
           {'Level': 3, 'LevelCode': '3', 'ColorCode': '#fdc503', 'IsActive': '1'},
           {'Level': 4, 'LevelCode': '4', 'ColorCode': '#d51f35', 'IsActive': '1'},
           {'Level': 5, 'LevelCode': '5', 'ColorCode': '#d51f35', 'IsActive': '1'},
       ]
    )

def downgrade():
    op.drop_table('HardwareFaultLevelInfo')
