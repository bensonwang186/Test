import datetime
import os
import sys
# sys.path.append("C:\\Users\\ricky_chen\Documents\GitHub\\mobile")
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

from System import settings, systemFunction

Base = declarative_base()

def insert_init_data():
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
        config.selfTestTime = None
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
        energyCost0.endTime = datetime.datetime(1, 1, 1, 0, 0)
        energyCost0.cost = float(0.12)

        energySetting.energyCost.append(energyCost0)
        session.add(energySetting)

        # </editor-fold>

        session.commit()
        session.close()

    except Exception:
        print("dbInit failed")
        traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    insert_init_data()