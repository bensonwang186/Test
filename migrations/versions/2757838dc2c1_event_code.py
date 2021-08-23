"""event code

Revision ID: 2757838dc2c1
Revises: e79180543be3
Create Date: 2020-03-06 12:18:48.490015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME


# revision identifiers, used by Alembic.
revision = '2757838dc2c1'
down_revision = '7f7c1f403ab1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('EventLog', sa.Column('isHwFault', BOOLEAN))
    op.add_column('EventLog', sa.Column('levelCode', TEXT))
    op.add_column('EventLog', sa.Column('errorCode', TEXT))

    hardwareFaultCodeInfoTable = op.create_table('HardwareFaultCodeInfo',
        sa.Column('Id', INTEGER, autoincrement=True, primary_key=True),
        sa.Column('ErrorCode', TEXT, nullable=False),
        sa.Column('Description', TEXT, nullable=False),
        sa.Column('Note', TEXT),
        sa.Column('IsActive', BOOLEAN, nullable=False)
    )

    op.bulk_insert(hardwareFaultCodeInfoTable,
       [
           {'ErrorCode': 'C01', 'Description': 'Battery Over Charge ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C02', 'Description': 'Charger Fail to charge Battery', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C04', 'Description': 'Battery Low', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C05', 'Description': 'Battery (test) Failure', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C06', 'Description': 'Battery Disconnected', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C07', 'Description': 'Service Battery (=Replace Battery)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C08', 'Description': 'Cold start Battery voltage over', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C12', 'Description': 'Load Over Setting %', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C20', 'Description': 'Cold start output short', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C21', 'Description': 'Output Short ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C22', 'Description': 'Output Overload ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C23', 'Description': 'Over temperature (AVR Transformer)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C25', 'Description': 'EPO Off', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C26', 'Description': 'OCP (Output Current Protect)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C27', 'Description': 'ROO Off', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C29', 'Description': 'AVR fault', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C2A', 'Description': 'Vout AD fail ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C30', 'Description': 'Inverter Fault', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C31', 'Description': 'High Output V', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C32', 'Description': 'Low Output V', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C33', 'Description': 'Over Temperature (Heat-Sink)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C34', 'Description': 'Fan Error', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C35', 'Description': 'Fan Error (Rear) ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C36', 'Description': 'Fan Error (Middle)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C37', 'Description': 'Fan Error (Front) ', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C40', 'Description': 'Bus Fault', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C41', 'Description': 'Bus Fault +High', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C42', 'Description': 'Bus Fault +Low', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C43', 'Description': 'Bus Fault -High', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C44', 'Description': 'Bus Fault -Low', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C50', 'Description': 'Input Power Fail', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C51', 'Description': 'Input V+Hz out of range', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C52', 'Description': 'Input    V    out of range', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C53', 'Description': 'Input    Hz   out of range', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C54', 'Description': 'Line Abnormal (Auto-restart)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C55', 'Description': 'Wiring Fault', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C56', 'Description': 'ICP (Input Current Protect)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': 'C57', 'Description': 'Manual Bypass Forbidden (For OL6~10K)', 'Note': '', 'IsActive': 1},
           {'ErrorCode': '0', 'Description': 'Fault - Fan Error  - Front.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '1', 'Description': 'Fault - Fan Error  - Middle.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '2', 'Description': 'Fault - Fan Error  - Rear.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '3', 'Description': 'Warning - Fan Error - Front.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '4', 'Description': 'Warning - Fan Error - Middle.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '5', 'Description': 'Warning - Fan Error - Rear.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '6', 'Description': 'Fault - Output Short. (DS4.4)', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '7', 'Description': 'Fault – Output Overload. (DS4.2) (DS4.6)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '8', 'Description': 'Warning – Output Overload. (DS4.2) (DS4.6)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '9', 'Description': 'Warning - Output Over load threshold setting % (C26,P18).',
            'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '10', 'Description': 'Fault - Battery Voltage Over.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '11', 'Description': 'Warning – Battery Voltage Over.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '12', 'Description': 'Warning - Battery Voltage Under.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '13', 'Description': 'Warning - Test Battery Failure.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '14', 'Description': 'Warning - Battery Disconnected / Battery Missing.', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '15', 'Description': 'Warning - Charger Failure.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '16', 'Description': 'Fault - Transfer over temp.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '17', 'Description': 'Fault - Inverter over temp. (DS2.4)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '18', 'Description': 'Warning - Transfer over temp.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '19', 'Description': 'Warning - Inverter over temp. (DS2.4)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '20', 'Description': 'Fault - Relay Failure.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '21', 'Description': 'Warning - Relay Failure.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '22', 'Description': 'Warning - Wiring Fault.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '23', 'Description': 'Warning - EEPROM Failure.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '24', 'Description': 'Fault - EPO OFF (Emergency Power Off).', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '25', 'Description': 'Fault - ROO OFF (Remote On Off).', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '26', 'Description': 'Warning - Backfeed Active.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '27', 'Description': 'Warning - Manual Bypass Forbidden.', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '28', 'Description': 'Fault - Inverter - High Output voltage.(DS2.3)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '29', 'Description': 'Fault - Inverter - Low Output voltage.(DS2.3)', 'Note': 'oldCode',
            'IsActive': 1},
           {'ErrorCode': '30', 'Description': 'Fault -  High (+) DC Bus ', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '31', 'Description': 'Fault -  High (-) DC Bus ', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '32', 'Description': 'Fault -  Low (+) DC Bus ', 'Note': 'oldCode', 'IsActive': 1},
           {'ErrorCode': '33', 'Description': 'Fault -  Low (-) DC Bus ', 'Note': 'oldCode', 'IsActive': 1}
       ]
    )


def downgrade():
    op.drop_column('EventLog', 'isHwFault')
    op.drop_column('EventLog', 'levelCode')
    op.drop_column('EventLog', 'errorCode')
    op.drop_table('HardwareFaultCodeInfo')

