import os
import sys

sys.path.append(os.path.dirname(__file__).join('../..'))
print(sys.path)

import traceback
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

from model_Json.tables.Configuration import Configuration
from model_Json.tables.EmailNotification import EmailNotification
from model_Json.tables.OAuthCredentials import OAuthCredentials
from model_Json.tables.Schedule import Schedule
from model_Json.tables.EnergyCost import EnergySetting
from model_Json.tables.EnergyCost import EnergyCost

from System import settings, systemFunction

# configuration_table = table('Configuration',
#                             column('summaryFilter', INTEGER, nullable=True),
#                             column('summaryFilterTime', INTEGER, nullable=True),
#                             column('summaryFilter', INTEGER, nullable=True),
#                             column('softwareSoundEnable', BOOLEAN, nullable=True),
#                             column('softwareSoundTime', DATETIME, nullable=True),
#                             column('runtimeType', INTEGER, nullable=True),
#                             column('runtimeCountdownTime', INTEGER, nullable=True),
#                             column('runtimeTime', DATETIME, nullable=True),
#                             column('selfTestResult', BOOLEAN, nullable=True),
#                             column('selfTestTime', DATETIME, nullable=True),
#                             column('shutDownType', INTEGER, nullable=True),
#                             column('shutDownTime', DATETIME, nullable=True),
#                             column('IsActive', BOOLEAN, nullable=False))
#
# op.execute(configuration_table.insert().valueas(
#     {
#         'summaryFilter': 1,
#         'summaryFilterTime': None,
#         'softwareSoundEnable': True,
#         'softwareSoundTime': None,
#         'runtimeType': 0,
#         'runtimeCountdownTime': 5,
#         'runtimeTime': None,
#         'selfTestResult': True,
#         'selfTestTime': systemFunction.getDatetimeNonw(),
#         'shutDownType': 1,
#         'shutDownTime': None,
#         'IsActive': True
#     }
# ))

Base = declarative_base()

def insert_test_data():
    try:
        engine = create_engine(settings.PPPE_DB, echo=False)
        print(settings.PPPE_DB)
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
        config.selfTestTime = systemFunction.getDatetimeNonw()
        config.shutDownType = 1
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
        email.active = True
        email.serviceProvider = 0
        email.smtpServiceAddress = "smtp.gmail.com"
        email.securityConnection = 0
        email.servicePort = 587
        email.senderName = "heelo"
        email.senderEmailAddress = "heelo@test.com.tw"
        email.needAuth = True
        email.authAccount = "ppbetest@gmail.com"
        email.authPassword = "cyberpower2"
        email.receivers = "ricky.chen@cyberpower.com"

        oa = OAuthCredentials()
        oa.accessToken = "ya29.GltsBIe1VJ2XNgwIIqIsMTqtgxdLWzDCXjZOm032DJVMXPTnA9Yp4XY8m7ZEzPDkmRPFD9vGZ1OdiDQuio1kSKPy8UMiewgBGnDbwo77iwtmbKD4JWxzKq7U601z"
        oa.clientId = "897123839781-eie0s6lco28t2tvvfspj7qr5k53qoh9q.apps.googleusercontent.com"
        oa.clientSecret = "oAd54ls8v4khtc6CJfj5k0V1"
        oa.refreshToken = "1/SakTEKsjp_0CSUvq8yXdPjMCmwxlkw1sphTdqzUFTKk"
        oa.tokenExpiry = "2017-06-17T07:15:24Z"
        oa.tokenUri = "https://accounts.google.com/o/oauth2/token"
        oa.oauthUserEmail = "elmo_chang@cpsww.com.tw"
        session.add(email)
        session.add(oa)

        # </editor-fold>

        # <editor-fold desc="EnergySetting">

        energySetting = EnergySetting()
        energySetting.country = "AR"
        energySetting.co2EmittedKg = float(0.352)
        energySetting.co2EmittedLb = float(0.766)
        energySetting.measurement = 0
        energySetting.updateTime = None

        energyCost0 = EnergyCost()
        now = systemFunction.getDatetimeNonw()
        energyCost0.startTime = datetime.now() - timedelta(days=10)
        energyCost0.endTime = datetime.now() - timedelta(days=9)
        energyCost0.cost = float(0.21)

        energyCost1 = EnergyCost()
        energyCost1.startTime = datetime.now() - timedelta(days=8)
        energyCost1.endTime = datetime.now() - timedelta(days=7)
        energyCost1.cost = float(0.31)

        energyCost2 = EnergyCost()
        energyCost2.startTime = datetime.now() - timedelta(days=6)
        energyCost2.endTime = datetime.now() - timedelta(days=5)
        energyCost2.cost = float(0.41)

        energyCost3 = EnergyCost()
        energyCost3.startTime = datetime.now() - timedelta(days=1)
        energyCost3.endTime = now.replace(hour=0, minute=0, second=00, microsecond=00)
        energyCost3.cost = float(0.51)

        energySetting.energyCost.append(energyCost0)
        energySetting.energyCost.append(energyCost1)
        energySetting.energyCost.append(energyCost2)
        energySetting.energyCost.append(energyCost3)
        # energyCost0.energySettingId = energySetting.id
        # energyCost1.energySettingId = energySetting.id
        # energyCost2.energySettingId = energySetting.id
        # energyCost3.energySettingId = energySetting.id

        session.add(energySetting)

        # </editor-fold>
        session.commit()
        session.close()

    except Exception:
        print("dbInit failed")
        traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    insert_test_data()