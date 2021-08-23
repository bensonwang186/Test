"""add device log

Revision ID: 7f7c1f403ab1
Revises: e79180543be3
Create Date: 2019-06-26 17:23:51.814066

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME

# revision identifiers, used by Alembic.
revision = '7f7c1f403ab1'
down_revision = 'e79180543be3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('DeviceLog', sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                    sa.Column('dsn', TEXT),
                    sa.Column('LocalTime', DATETIME, nullable=False),
                    sa.Column('ts', INTEGER, nullable=False),
                    sa.Column('dcode', INTEGER),
                    sa.Column('InSta', INTEGER),
                    sa.Column('InVolt', FLOAT),
                    sa.Column('InFreq', FLOAT),
                    sa.Column('OutSta', INTEGER),
                    sa.Column('OutVolt', FLOAT),
                    sa.Column('OutFreq', FLOAT),
                    sa.Column('OutCur', FLOAT),
                    sa.Column('BatSta', INTEGER),
                    sa.Column('BatCap', FLOAT),
                    sa.Column('BatRun', FLOAT),
                    sa.Column('BatVolt', FLOAT),
                    sa.Column('BatWar', INTEGER),
                    sa.Column('SysSta', TEXT),
                    sa.Column('SysTemp', FLOAT),
                    sa.Column('EnvTemp', FLOAT),
                    sa.Column('EnvHumi', FLOAT),
                    sa.Column('SN', TEXT),
                    sa.Column('rFV', TEXT),
                    sa.Column('rSN', TEXT),
                    sa.Column('ReDate', TEXT),
                    sa.Column('LP', INTEGER),
                    sa.Column('Model', TEXT),
                    sa.Column('FV', TEXT),
                    sa.Column('RatPow', INTEGER),
                    sa.Column('VoltRat', INTEGER),
                    sa.Column('WorFreq', TEXT),
                    sa.Column('upsState', INTEGER),
                    sa.Column('Type', INTEGER),
                    sa.Column('Event', TEXT),
                    sa.Column('NclOut', TEXT),
                    sa.Column('DevOut', INTEGER),
                    sa.Column('PowSour', INTEGER),
                    sa.Column('Dev', INTEGER),
                    sa.Column('DevLoad', FLOAT),
                    sa.Column('BatVoltRat', INTEGER),
                    sa.Column('lFV', TEXT),
                    sa.Column('uFV', TEXT),
                    sa.Column('ExtData', TEXT)
                    )

    op.add_column('Configuration', sa.Column('isBattNeedReplaced', BOOLEAN, nullable=False, server_default=sa.schema.DefaultClause("0")))

    with op.batch_alter_table('Configuration') as batch_op:
        batch_op.alter_column(column_name='customUpsName', type_=TEXT, existing_type=BOOLEAN)

def downgrade():
    op.drop_table('DeviceLog')

    with op.batch_alter_table('Configuration') as batch_op:
        batch_op.drop_column('isBattNeedReplaced')
        batch_op.alter_column(column_name='customUpsName', type_=BOOLEAN, existing_type=TEXT)

