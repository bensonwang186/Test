"""init db

Revision ID: e4f52af076bc
Revises: 
Create Date: 2017-08-08 16:45:45.193351

"""
import sys
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import BOOLEAN
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.dialects.sqlite import FLOAT
from sqlalchemy.dialects.sqlite import TEXT
import traceback

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

from model_Json.tables.Configuration import Configuration
from model_Json.tables.EmailNotification import EmailNotification
from model_Json.tables.OAuthCredentials import OAuthCredentials
from model_Json.tables.Schedule import Schedule
from model_Json.tables.EnergyCost import EnergySetting
from model_Json.tables.EnergyCost import EnergyCost
from views.Custom.CountryTableData import CountryTable
from views.Custom.ViewData import CO2MeasurementUnit
from System import settings, systemFunction

Base = declarative_base()

# revision identifiers, used by Alembic.
revision = 'e4f52af076bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    configurationTable = op.create_table('Configuration',
                                         sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                         sa.Column('summaryFilter', INTEGER, nullable=True),
                                         sa.Column('summaryFilterTime', DATETIME, nullable=True),
                                         sa.Column('softwareSoundEnable', BOOLEAN, nullable=True),
                                         sa.Column('softwareSoundTime', DATETIME, nullable=True),
                                         sa.Column('runtimeType', INTEGER, nullable=True),
                                         sa.Column('runtimeCountdownTime', INTEGER, nullable=True),
                                         sa.Column('runtimeTime', DATETIME, nullable=True),
                                         sa.Column('selfTestResult', BOOLEAN, nullable=True),
                                         sa.Column('selfTestTime', DATETIME, nullable=True),
                                         sa.Column('shutDownType', INTEGER, nullable=True),
                                         sa.Column('shutDownTime', DATETIME, nullable=True),
                                         sa.Column('IsActive', BOOLEAN, nullable=False)
                                         )
    emailNotificationTable = op.create_table('EmailNotification',
                                             sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                             sa.Column('active', BOOLEAN, nullable=False),
                                             sa.Column('serviceProvider', INTEGER, nullable=False),
                                             sa.Column('smtpServiceAddress', TEXT, nullable=True),
                                             sa.Column('securityConnection', INTEGER, nullable=True),
                                             sa.Column('servicePort', INTEGER, nullable=True),
                                             sa.Column('senderName', TEXT, nullable=True),
                                             sa.Column('senderEmailAddress', TEXT, nullable=True),
                                             sa.Column('needAuth', BOOLEAN, nullable=True),
                                             sa.Column('authAccount', TEXT, nullable=True),
                                             sa.Column('authPassword', TEXT, nullable=True),
                                             sa.Column('receivers', TEXT, nullable=True),
                                             sa.Column('isApplied', BOOLEAN, nullable=False)
                                             )
    energyConsumptionTable = op.create_table('EnergyConsumption',
                                             sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                             sa.Column('consumption', FLOAT, nullable=True),
                                             sa.Column('createTime', DATETIME, nullable=True)
                                             )
    energySettingTable = op.create_table('EnergySetting',
                                         sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                         sa.Column('country', TEXT, nullable=True),
                                         sa.Column('co2EmittedKg', FLOAT, nullable=True),
                                         sa.Column('co2EmittedLb', FLOAT, nullable=True),
                                         sa.Column('measurement', INTEGER, nullable=True),
                                         sa.Column('updateTime', DATETIME, nullable=True)
                                         )
    energyCostTable = op.create_table('EnergyCost',
                                      sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                      sa.Column('startTime', DATETIME, nullable=True),
                                      sa.Column('endTime', DATETIME, nullable=True),
                                      sa.Column('cost', FLOAT, nullable=True),
                                      sa.Column('energySettingId', INTEGER),
                                      sa.Column('updateTime', DATETIME, nullable=True)
                                      )
    with op.batch_alter_table('EnergyCost') as batch_op:
        batch_op.create_foreign_key('fk_energySetting', 'EnergySetting', ['energySettingId'], ['id'])

    oAuthCredentialsTable = op.create_table('OAuthCredentials',
                                            sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                            sa.Column('accessToken', TEXT, nullable=True),
                                            sa.Column('clientId', TEXT, nullable=True),
                                            sa.Column('clientSecret', TEXT, nullable=True),
                                            sa.Column('refreshToken', TEXT, nullable=True),
                                            sa.Column('tokenExpiry', TEXT, nullable=True),
                                            sa.Column('tokenUri', TEXT, nullable=True),
                                            sa.Column('oauthUserEmail', TEXT, nullable=True)
                                            )
    scheduleTable = op.create_table('Schedule',
                                    sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                    sa.Column('days', TEXT, nullable=True),
                                    sa.Column('onTime', DATETIME, nullable=True),
                                    sa.Column('onAction', BOOLEAN, nullable=True),
                                    sa.Column('offTime', DATETIME, nullable=True),
                                    sa.Column('offAction', BOOLEAN, nullable=True),
                                    sa.Column('noneReset', BOOLEAN, nullable=True),
                                    sa.Column('updateTime', DATETIME, nullable=True)
                                    )

    eventLogTable = op.create_table('EventLog',
                                    sa.Column('id', INTEGER, autoincrement=True, primary_key=True),
                                    sa.Column('EventId', INTEGER, nullable=True),
                                    sa.Column('CreateTime', DATETIME, nullable=True),
                                    sa.Column('Duration', INTEGER, nullable=True)
                                    )

    # Configuration
    op.execute(configurationTable.insert().values(
        {"summaryFilter": 1, "summaryFilterTime": None, "softwareSoundEnable": True, "softwareSoundTime": None,
         "runtimeType": 0,
         "runtimeCountdownTime": 5, "runtimeTime": None, "selfTestResult": True, "selfTestTime": None,
         "shutDownType": 0, "shutDownTime": None, "IsActive": True}))

    # Schedule
    dic = systemFunction.getNext7Weekdays()
    days0 = settings.week[0]
    onTime0 = systemFunction.nextWeekDayTime(dic[days0].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime0 = systemFunction.nextWeekDayTime(dic[days0].replace(hour=17, minute=00, second=00, microsecond=00))

    days1 = settings.week[1]
    onTime1 = systemFunction.nextWeekDayTime(dic[days1].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime1 = systemFunction.nextWeekDayTime(dic[days1].replace(hour=17, minute=00, second=00, microsecond=00))

    days2 = settings.week[2]
    onTime2 = systemFunction.nextWeekDayTime(dic[days2].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime2 = systemFunction.nextWeekDayTime(dic[days2].replace(hour=17, minute=00, second=00, microsecond=00))

    days3 = settings.week[3]
    onTime3 = systemFunction.nextWeekDayTime(dic[days3].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime3 = systemFunction.nextWeekDayTime(dic[days3].replace(hour=17, minute=00, second=00, microsecond=00))

    days4 = settings.week[4]
    onTime4 = systemFunction.nextWeekDayTime(dic[days4].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime4 = systemFunction.nextWeekDayTime(dic[days4].replace(hour=17, minute=00, second=00, microsecond=00))

    days5 = settings.week[5]
    onTime5 = systemFunction.nextWeekDayTime(dic[days5].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime5 = systemFunction.nextWeekDayTime(dic[days5].replace(hour=17, minute=00, second=00, microsecond=00))

    days6 = settings.week[6]
    onTime6 = systemFunction.nextWeekDayTime(dic[days6].replace(hour=9, minute=00, second=00, microsecond=00))
    offTime6 = systemFunction.nextWeekDayTime(dic[days6].replace(hour=17, minute=00, second=00, microsecond=00))

    op.bulk_insert(scheduleTable,
                   [
                       {"days": days0, "onTime": onTime0, "onAction": None, "offTime": offTime0, "noneReset": None,
                        "updateTime": None},
                       {"days": days1, "onTime": onTime1, "onAction": None, "offTime": offTime1, "noneReset": None,
                        "updateTime": None},
                       {"days": days2, "onTime": onTime2, "onAction": None, "offTime": offTime2, "noneReset": None,
                        "updateTime": None},
                       {"days": days3, "onTime": onTime3, "onAction": None, "offTime": offTime3, "noneReset": None,
                        "updateTime": None},
                       {"days": days4, "onTime": onTime4, "onAction": None, "offTime": offTime4, "noneReset": None,
                        "updateTime": None},
                       {"days": days5, "onTime": onTime5, "onAction": None, "offTime": offTime5, "noneReset": None,
                        "updateTime": None},
                       {"days": days6, "onTime": onTime6, "onAction": None, "offTime": offTime6, "noneReset": None,
                        "updateTime": None}
                   ]
                   )

    op.execute(emailNotificationTable.insert().values(
        {"active": False, "serviceProvider": 0, "smtpServiceAddress": None, "securityConnection": None,
         "servicePort": 587, "senderName": None, "senderEmailAddress": None,
         "needAuth": True, "authAccount": None, "authPassword": None, "receivers": None, "isApplied": False}))

    op.execute(oAuthCredentialsTable.insert().values(
        {"accessToken": None, "clientId": None, "clientSecret": None, "refreshToken": None, "tokenExpiry": None,
         "tokenUri": None, "oauthUserEmail": None}))

    mappingData = CountryTable().displayData["US"]
    op.execute(energySettingTable.insert().values(
        {"country": "US", "co2EmittedKg": mappingData.co2EmittedKg, "co2EmittedLb": None, "measurement": CO2MeasurementUnit.Kilograms.value, "updateTime": None}))

    now = systemFunction.getDatetimeNonw()
    op.execute(energyCostTable.insert().values(
        {"startTime": now.replace(hour=00, minute=00, second=00, microsecond=00), "endTime": now, "energySettingId": 1,
         "cost": float(0.12)}))


    # insert_init_data()


def insert_init_data():
    try:
        engine = create_engine(settings.PPPE_DB, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # <editor-fold desc="Configuration">

        config = Configuration()
        config.summaryFilter = 1
        config.summaryFilterTime = None
        config.softwareSoundEnable = True
        config.softwareSoundTime = None
        config.runtimeType = 0
        config.runtimeCountdownTime = 5
        config.runtimeTime = None
        config.selfTestResult = True
        config.selfTestTime = None
        config.shutDownType = 0
        config.shutDownTime = None
        config.IsActive = True
        session.add(config)

        # </editor-fold>

        # <editor-fold desc="Schedule">

        dic = systemFunction.getNext7Weekdays()

        scheduleMon = Schedule()
        scheduleMon.days = settings.week[0]
        scheduleMon.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleMon.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleMon.onAction = None
        scheduleMon.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleMon.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleMon.noneReset = None
        scheduleMon.updateTime = None
        session.add(scheduleMon)

        scheduleTue = Schedule()
        scheduleTue.days = settings.week[1]
        scheduleTue.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleTue.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleTue.onAction = None
        scheduleTue.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleTue.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleTue.offAction = None
        scheduleTue.noneReset = None
        scheduleTue.updateTime = None
        session.add(scheduleTue)

        scheduleWed = Schedule()
        scheduleWed.days = settings.week[2]
        scheduleWed.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleWed.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleWed.onAction = None
        scheduleWed.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleWed.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleWed.offAction = None
        scheduleWed.noneReset = None
        scheduleWed.updateTime = None
        session.add(scheduleWed)

        scheduleThu = Schedule()
        scheduleThu.days = settings.week[3]
        scheduleThu.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleThu.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleThu.onAction = None
        scheduleThu.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleThu.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleThu.offAction = None
        scheduleThu.noneReset = None
        scheduleThu.updateTime = None
        session.add(scheduleThu)

        scheduleFri = Schedule()
        scheduleFri.days = settings.week[4]
        scheduleFri.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleFri.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleFri.onAction = None
        scheduleFri.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleFri.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleFri.offAction = None
        scheduleFri.noneReset = None
        scheduleFri.updateTime = None
        session.add(scheduleFri)

        scheduleSat = Schedule()
        scheduleSat.days = settings.week[5]
        scheduleSat.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleSat.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleSat.onAction = None
        scheduleSat.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleSat.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleSat.offAction = None
        scheduleSat.noneReset = None
        scheduleSat.updateTime = None
        session.add(scheduleSat)

        scheduleSun = Schedule()
        scheduleSun.days = settings.week[6]
        scheduleSun.onTime = systemFunction.nextWeekDayTime(
            dic[scheduleSun.days].replace(hour=9, minute=00, second=00, microsecond=00))
        scheduleSun.onAction = None
        scheduleSun.offTime = systemFunction.nextWeekDayTime(
            dic[scheduleSun.days].replace(hour=17, minute=00, second=00, microsecond=00))
        scheduleSun.offAction = None
        scheduleSun.noneReset = None
        scheduleSun.updateTime = None
        session.add(scheduleSun)

        # </editor-fold>

        # <editor-fold desc="Email">

        email = EmailNotification()
        email.active = False
        email.serviceProvider = 0
        email.smtpServiceAddress = None
        email.securityConnection = None
        email.servicePort = 587
        email.senderName = None
        email.senderEmailAddress = None
        email.needAuth = True
        email.authAccount = None
        email.authPassword = None
        email.receivers = None
        email.isApplied = False

        oa = OAuthCredentials()
        oa.accessToken = None
        oa.clientId = None
        oa.clientSecret = None
        oa.refreshToken = None
        oa.tokenExpiry = None
        oa.tokenUri = None
        oa.oauthUserEmail = None
        session.add(email)
        session.add(oa)

        # </editor-fold>

        # <editor-fold desc="EnergySetting">

        energySetting = EnergySetting()
        energySetting.country = "US"
        energySetting.co2EmittedKg = None
        energySetting.co2EmittedLb = None
        energySetting.measurement = None
        energySetting.updateTime = None

        energyCost0 = EnergyCost()
        now = systemFunction.getDatetimeNonw()
        energyCost0.startTime = now.replace(hour=00, minute=00, second=00, microsecond=00)
        energyCost0.endTime = now
        energyCost0.cost = float(0.12)

        energySetting.energyCost.append(energyCost0)
        session.add(energySetting)

        # </editor-fold>

        session.commit()
        session.close()

    except Exception:
        print("dbInit failed")
        traceback.print_exc(file=sys.stdout)

def downgrade():
    op.drop_table('Configuration')
    op.drop_table('EmailNotification')
    op.drop_table('EnergyConsumption')
    op.drop_table('EnergySetting')
    op.drop_table('EnergyCost')
    op.drop_table('OAuthCredentials')
    op.drop_table('Schedule')
    op.drop_table('EventLog')
