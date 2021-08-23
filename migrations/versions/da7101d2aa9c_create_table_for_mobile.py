"""Create table for mobile

Revision ID: da7101d2aa9c
Revises: 5bd34854eae2
Create Date: 2018-03-05 17:39:52.515559

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.dialects.sqlite import BOOLEAN
from Utility import DataCryptor
from System.settings import EMQ_ACC, EMQ_PWD


# revision identifiers, used by Alembic.
revision = 'da7101d2aa9c'
down_revision = '5bd34854eae2'
branch_labels = None
depends_on = None


def upgrade():
    account = op.create_table('Account',
                              sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                              sa.Column('accountId', TEXT, nullable=True),
                              sa.Column('accountSecret', TEXT, nullable=True),
                              sa.Column('fcmApiKey', TEXT, nullable=True),
                              sa.Column('emqAcc', TEXT, nullable=True),
                              sa.Column('emqSecret', TEXT, nullable=True),
                              sa.Column('acode', INTEGER, nullable=True)
                              )

    # insert account default value and encrypt
    cyptor = DataCryptor.Cryptor()
    op.execute(account.insert().values({"accountId": None, "accountSecret": None, "fcmApiKey": None,
                                        "emqAcc": cyptor.enc(EMQ_ACC), "emqSecret": cyptor.enc(EMQ_PWD), "acode": None}))

    op.add_column('Configuration', sa.Column('mobileSolutionEnable', BOOLEAN, nullable=False, server_default=sa.schema.DefaultClause("0")))
    op.add_column('Configuration', sa.Column('customUpsName', BOOLEAN, nullable=True))


def downgrade():
    op.drop_table('Account')
    op.drop_column('Configuration', 'mobileSolutionEnable')
    op.drop_column('Configuration', 'customUpsName')
