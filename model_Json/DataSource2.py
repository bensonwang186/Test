# -*- coding: utf-8 -*-
import datetime
import sys, json
import traceback
from enum import Enum
from operator import attrgetter
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

from Events.Event import EventID
from System import settings, systemFunction
from model_Json import DBSession
from model_Json.tables.Configuration import Configuration
from model_Json.tables.EmailNotification import EmailNotification
from model_Json.tables.EnergyConsumption import EnergyConsumption
from model_Json.tables.EnergyCost import EnergyCost
from model_Json.tables.EnergyCost import EnergySetting
from model_Json.tables.EventLog import EventLog, EventEnum
from model_Json.tables.OAuthCredentials import OAuthCredentials
from model_Json.tables.Schedule import Schedule
from model_Json.tables.Account import Account
from model_Json.tables.DeviceLog import DeviceLog
from model_Json.tables.HardwareFault import HardwareFaultCodeInfo, HardwareFaultLevelInfo
from i18n import i18nId, appLocaleData
from Utility import DataCryptor, i18nTranslater
from views.Custom.ViewData import ErrorCodeEventNumber
from itertools import islice

Base = declarative_base()


class DataSource2(QObject):
    # updateSettingSignal = pyqtSignal(object)
    updateEmailNotificationSignal = pyqtSignal(object, object)
    updateConfigSettingSignal = pyqtSignal(object)
    updateEventLogSignal = pyqtSignal(object)  # for summary page
    configurationSettingUpdateSignal = pyqtSignal(object)
    runtimeChangeConfigSignal = pyqtSignal(object)
    updateEventLogsPageSignal = pyqtSignal(object)  # for event logs page

    def __init__(self):
        super(DataSource2, self).__init__()

        self.emailNotification = None
        self.oauthCredentials = None
        self.configurationSetting = self.readActiveConfig()
        self.energySetting = self.readEnergySetting()
        self.lastEventFilter = None  # 紀錄view上次所選filter
        self.lastEventFilter = None
        # self.allEventCodes = self.readAllEventCode()
        self.allEventLvCodes = self.readAllEventLevelCode() # dict
        self.allEventEnum = self.readAllEventEnum() # dict

    @QtCore.pyqtSlot(object)
    def updatePropertiesSignal(self, settingData):
        self.updateSettingSignal.emit(settingData)

    @QtCore.pyqtSlot(object)
    def addAnEventLog(self, eventId, Duration, isHwFault=None, levelCode=None, errorCode=None):

        with DBSession.db_session(settings.PPPE_DB) as session:

            # cnt = session.query(EventLog).count()
            # if cnt > 0 and cnt > settings.EVENT_LOG_LIMIT:
            #     log = session.query(EventLog).first()
            #     session.delete(log)
            #     session.commit()

            createTime = systemFunction.getDatetimeNonw()
            # newLog = EventLog(eventId, createTime, Duration)
            newLog = EventLog()
            newLog.EventId = eventId
            newLog.CreateTime = createTime
            newLog.Duration = Duration
            newLog.isHwFault = isHwFault
            newLog.levelCode = levelCode
            newLog.errorCode = errorCode

            session.add(newLog)
            session.commit()

        self.updateEventLogsPageSignal.emit(self.lastEventFilter)

    def queryEmailNotification(self):
        with DBSession.db_session(settings.PPPE_DB) as session:
            # try:
            self.emailNotification = session.query(EmailNotification).first()
            if self.emailNotification is None:
                self.emailNotification = EmailNotification()

    def queryOAuthCredentials(self):
        with DBSession.db_session(settings.PPPE_DB) as session:
            # try:
            self.oauthCredentials = session.query(OAuthCredentials).first()
            if self.oauthCredentials is None:
                self.oauthCredentials = OAuthCredentials()

    def restore(self):
        self.queryEmailNotification()
        self.queryOAuthCredentials()
        self.updateEmailNotificationSignal.emit(self.emailNotification, self.oauthCredentials)
        self.updateConfigSettingSignal.emit(self.configurationSetting)

    def setEmailNotification(self, emailNotification):
        with DBSession.db_session(settings.PPPE_DB) as session:
            sqlData = session.query(EmailNotification).first()
            if sqlData is None:
                emailData = EmailNotification()
                if emailNotification.active is not None:
                    emailData.active = self.emailNotification.active = emailNotification.active
                if emailNotification.serviceProvider is not None:
                    emailData.serviceProvider = self.emailNotification.serviceProvider = emailNotification.serviceProvider
                if emailNotification.smtpServiceAddress is not None:
                    emailData.smtpServiceAddress = self.emailNotification.smtpServiceAddress = emailNotification.smtpServiceAddress.strip()
                if emailNotification.securityConnection is not None:
                    emailData.securityConnection = self.emailNotification.securityConnection = emailNotification.securityConnection
                if emailNotification.servicePort is not None:
                    emailData.servicePort = self.emailNotification.servicePort = emailNotification.servicePort
                if emailNotification.senderName is not None:
                    emailData.senderName = self.emailNotification.senderName = emailNotification.senderName
                if emailNotification.senderEmailAddress is not None:
                    emailData.senderEmailAddress = self.emailNotification.senderEmailAddress = emailNotification.senderEmailAddress
                if emailNotification.needAuth is not None:
                    emailData.needAuth = self.emailNotification.needAuth = emailNotification.needAuth
                if emailNotification.authAccount is not None:
                    emailData.authAccount = self.emailNotification.authAccount = emailNotification.authAccount
                if emailNotification.authPassword is not None:
                    emailData.authPassword = self.emailNotification.authPassword = emailNotification.authPassword
                if emailNotification.receivers is not None:
                    emailData.receivers = self.emailNotification.receivers = emailNotification.receivers
                if emailNotification.isApplied is not None:
                    emailData.isApplied = self.emailNotification.isApplied = emailNotification.isApplied
                session.add(emailData)
            else:
                if emailNotification.active is not None:
                    sqlData.active = self.emailNotification.active = emailNotification.active
                if emailNotification.serviceProvider is not None:
                    sqlData.serviceProvider = self.emailNotification.serviceProvider = emailNotification.serviceProvider
                if emailNotification.smtpServiceAddress is not None:
                    sqlData.smtpServiceAddress = self.emailNotification.smtpServiceAddress = emailNotification.smtpServiceAddress.strip()
                if emailNotification.securityConnection is not None:
                    sqlData.securityConnection = self.emailNotification.securityConnection = emailNotification.securityConnection
                if emailNotification.servicePort is not None:
                    sqlData.servicePort = self.emailNotification.servicePort = emailNotification.servicePort
                if emailNotification.senderName is not None:
                    sqlData.senderName = self.emailNotification.senderName = emailNotification.senderName
                if emailNotification.senderEmailAddress is not None:
                    sqlData.senderEmailAddress = self.emailNotification.senderEmailAddress = emailNotification.senderEmailAddress
                if emailNotification.needAuth is not None:
                    sqlData.needAuth = self.emailNotification.needAuth = emailNotification.needAuth
                if emailNotification.authAccount is not None:
                    sqlData.authAccount = self.emailNotification.authAccount = emailNotification.authAccount
                if emailNotification.authPassword is not None:
                    sqlData.authPassword = self.emailNotification.authPassword = emailNotification.authPassword
                if emailNotification.receivers is not None:
                    sqlData.receivers = self.emailNotification.receivers = emailNotification.receivers
                if emailNotification.isApplied is not None:
                    sqlData.isApplied = self.emailNotification.isApplied = emailNotification.isApplied

            session.commit()
            session.close()

    def setOAuthCredentials(self, oauthCredentials):
        if oauthCredentials == None:
            return
        with DBSession.db_session(settings.PPPE_DB) as session:
            sqlData = session.query(OAuthCredentials).first()
            if sqlData is None:
                oauthData = OAuthCredentials()
                cyptor = DataCryptor.Cryptor()
                accessTokeEnc = cyptor.enc(oauthCredentials.accessToken)
                oauthData.accessToken = self.oauthCredentials.accessToken = accessTokeEnc

                clientIdEnc = cyptor.enc(oauthCredentials.clientId)
                oauthData.clientId = self.oauthCredentials.clientId = clientIdEnc

                clientSecretEnc = cyptor.enc(oauthCredentials.clientSecret)
                oauthData.clientSecret = self.oauthCredentials.clientSecret = clientSecretEnc

                refreshTokenEnc = cyptor.enc(oauthCredentials.refreshToken)
                oauthData.refreshToken = self.oauthCredentials.refreshToken = refreshTokenEnc

                tokenExpiryEnc = cyptor.enc(oauthCredentials.tokenExpiry)
                oauthData.tokenExpiry = self.oauthCredentials.tokenExpiry = tokenExpiryEnc

                tokenUriEnc = cyptor.enc(oauthCredentials.tokenUri)
                oauthData.tokenUri = self.oauthCredentials.tokenUri = tokenUriEnc
                oauthData.oauthUserEmail = self.oauthCredentials.oauthUserEmail = oauthCredentials.oauthUserEmail
                session.add(oauthData)
            else:
                cyptor = DataCryptor.Cryptor()

                accessTokeEnc = cyptor.enc(oauthCredentials.accessToken)
                sqlData.accessToken = self.oauthCredentials.accessToken = accessTokeEnc

                clientIdEnc = cyptor.enc(oauthCredentials.clientId)
                sqlData.clientId = self.oauthCredentials.clientId = clientIdEnc

                clientSecretEnc = cyptor.enc(oauthCredentials.clientSecret)
                sqlData.clientSecret = self.oauthCredentials.clientSecret = clientSecretEnc

                refreshTokenEnc = cyptor.enc(oauthCredentials.refreshToken)
                sqlData.refreshToken = self.oauthCredentials.refreshToken = refreshTokenEnc

                sqlData.tokenExpiry = self.oauthCredentials.tokenExpiry = oauthCredentials.tokenExpiry

                tokenUriEnc = cyptor.enc(oauthCredentials.tokenUri)
                sqlData.tokenUri = self.oauthCredentials.tokenUri = tokenUriEnc
                sqlData.oauthUserEmail = self.oauthCredentials.oauthUserEmail = oauthCredentials.oauthUserEmail

            session.commit()
            session.close()

    def updateEventLogDuration(self, eventId):
        """update an event log in db (for calculate event duration)"""

        with DBSession.db_session(settings.PPPE_DB) as session:
            lastEvent = session.query(EventLog).filter(EventLog.EventId == str(eventId)).order_by(
                EventLog.id.desc()).first()  # find the last record

            if lastEvent is not None:
                now = systemFunction.getDatetimeNonw()
                startTime = lastEvent.CreateTime
                lastEvent.Duration = int(
                    (now - startTime).total_seconds())  # compute differences between two dates in seconds
                session.commit()

        self.updateEventLogSignal.emit(True)
        self.updateEventLogsPageSignal.emit(self.lastEventFilter)

    def readActiveConfig(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                config = session.query(Configuration).filter(Configuration.IsActive).first()
        except Exception:
            traceback.print_exc(file=sys.stdout)

        return config

    def readAllConfig(self):
        with DBSession.db_session(settings.PPPE_DB) as session:
            activeList = session.query(self.Configuration).all()

        return activeList

    def updateDeviceConfig(self, data):

        now = systemFunction.getDatetimeNonw()

        with DBSession.db_session(settings.PPPE_DB) as session:
            config = session.query(Configuration).filter(Configuration.IsActive).first()

            if config is not None:

                if data.summaryFilter is not None:
                    config.summaryFilter = data.summaryFilter
                    config.summaryFilterTime = now

                if data.softwareSoundEnable is not None:
                    config.softwareSoundEnable = data.softwareSoundEnable
                    config.softwareSoundTime = now

                if data.runtimeType is not None:
                    config.runtimeType = data.runtimeType
                    config.runtimeCountdownTime = data.runtimeCountdownTime
                    config.runtimeTime = now

                if data.selfTestResult is not None:
                    config.selfTestResult = data.selfTestResult
                    config.selfTestTime = now

                if data.shutDownType is not None:
                    config.shutDownType = data.shutDownType
                    config.shutDownTime = now

                if data.IsActive is not None:
                    config.IsActive = data.IsActive

                if data.mobileSolutionEnable is not None:
                    config.mobileSolutionEnable = data.mobileSolutionEnable

                if data.customUpsName is not None:
                    config.customUpsName = data.customUpsName

                if data.langSetting is not None:
                    config.langSetting = data.langSetting

                if data.isBattNeedReplaced is not None:
                    config.isBattNeedReplaced = data.isBattNeedReplaced

                if data.updateResult is not None:
                    config.updateResult = data.updateResult

                if data.agree_policy is not None:
                    config.agree_policy = data.agree_policy

                try:
                    session.commit()

                    self.configurationSetting.summaryFilter = config.summaryFilter
                    self.configurationSetting.summaryFilterTime = config.summaryFilterTime

                    self.configurationSetting.softwareSoundEnable = config.softwareSoundEnable
                    self.configurationSetting.softwareSoundTime = config.softwareSoundTime

                    self.configurationSetting.runtimeType = config.runtimeType
                    self.configurationSetting.runtimeCountdownTime = config.runtimeCountdownTime
                    self.configurationSetting.runtimeTime = config.runtimeTime
                    self.runtimeChangeConfigSignal.emit(self)

                    self.configurationSetting.selfTestResult = config.selfTestResult
                    self.configurationSetting.selfTestTime = config.selfTestTime

                    self.configurationSetting.shutDownType = config.shutDownType
                    self.configurationSetting.shutDownTime = config.shutDownTime

                    self.configurationSetting.IsActive = config.IsActive
                    self.configurationSetting.langSetting = config.langSetting
                    self.configurationSetting.updateResult = config.updateResult

                    self.configurationSetting.mobileSolutionEnable = config.mobileSolutionEnable
                    self.configurationSetting.customUpsName = config.customUpsName
                    self.configurationSetting.isBattNeedReplaced = config.isBattNeedReplaced
                    # self.configurationSettingUpdateSignal.emit(self.configurationSetting)

                    if systemFunction.stringIsNullorEmpty(config.langSetting) == False:
                        appLocaleData.appLocaleRecorderFromDB().appLocale = config.langSetting

                except Exception:
                    traceback.print_exc(file=sys.stdout)

        return now

    def queryEventLogByDuration(self, weeks):

        eventFilter = [
            EventID.ID_UTILITY_FAILURE.value,
            # EventID.ID_UTILITY_FAILURE_RESTORE.value,
            EventID.ID_AVR_BOOST_ACTIVE.value,
            EventID.ID_AVR_BUCK_ACTIVE.value,
            # EventID.ID_AVR_BOOST_RESTORE.value,
            # EventID.ID_AVR_BUCK_RESTORE.value,
            EventID.ID_UTILITY_TRANSFER_HIGH.value,
            # EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE.value,
            EventID.ID_UTILITY_TRANSFER_LOW.value
            # EventID.ID_UTILITY_TRANSFER_LOW_RESTORE.value
        ]

        with DBSession.db_session(settings.PPPE_DB) as session:
            endDate = systemFunction.getDatetimeNonw().replace(hour=23, minute=59, second=59)
            startDate = datetime.date.today() - datetime.timedelta(days=(weeks * 7))

            logs = session.query(EventLog.EventId, func.count(EventLog.EventId), func.sum(EventLog.Duration))\
                .filter(EventLog.EventId.in_(eventFilter))\
                .filter(EventLog.CreateTime.between(str(startDate), str(endDate)))\
                .group_by(EventLog.EventId).all()

            lastLog = session.query(EventLog).filter(EventLog.EventId.in_(eventFilter))\
                .filter(EventLog.CreateTime.between(str(startDate), str(endDate)))\
                .order_by(EventLog.id.desc()).first()

        return (logs, lastLog)

    def readScheduleSetting(self):
        with DBSession.db_session(settings.PPPE_DB) as session:
            result = session.query(Schedule).all()

            # <editor-fold desc="找離當日最近一筆開關機時間">

        shutdownSetting = None  # 離當日最近一筆關機時間
        restartSetting = None

        allOffSchedule = list(filter(lambda x: x.offAction, result))
        if len(allOffSchedule) > 0:
            shutdownSetting = min(allOffSchedule,
                                  key=attrgetter('offTime'))  # Python min function with a list of objects

            if shutdownSetting.noneReset is False: # 由離當日最近一筆關機時間有無NR來決定是否重開機
                allOnSchedule = list(filter(lambda x: x.onAction, result))
                if len(allOnSchedule) > 0:
                    restartSetting = min(allOnSchedule,
                                         key=attrgetter('onTime'))  # Python min function with a list of objects

        return (result, shutdownSetting, restartSetting)

        # </editor-fold>

    def updateScheduleSetting(self, dataDic):
        nextWeekDaysDic = systemFunction.getNext7Weekdays()
        now = systemFunction.getDatetimeNonw()

        with DBSession.db_session(settings.PPPE_DB) as session:
            schedule1stQuery = session.query(Schedule).all()

            # 先在第一個loop 更新所有屬性(除了ontime)
            for item in schedule1stQuery:
                updateData = dataDic[item.days]
                offTime = nextWeekDaysDic[item.days].replace(hour=updateData.offTimeHour,
                                                             minute=updateData.offTimeMin, second=00,
                                                             microsecond=00)

                item.offTime = systemFunction.nextWeekDayTime(offTime)
                item.onAction = updateData.onAction
                item.offAction = updateData.offAction
                item.noneReset = updateData.noneReset
                item.updateTime = now

            session.commit()

            schedule2ndQuery = session.query(Schedule).all()
            shutdownSetting = None  # 離當日最近一筆關機時間
            allOffSchedule = list(filter(lambda x: x.offAction, schedule2ndQuery))

            if len(allOffSchedule) > 0:
                shutdownSetting = min(allOffSchedule,
                                      key=attrgetter('offTime'))  # Python min function with a list of objects

                # 在第二個loop更新ontime, 因ontime受offTime影響, 須待offTime先寫入, 才能更新
            for x in schedule2ndQuery:
                updateData = dataDic[x.days]
                ontime = nextWeekDaysDic[x.days].replace(hour=updateData.onTimeHour,
                                                         minute=updateData.onTimeMin, second=00, microsecond=00)

                if shutdownSetting is not None:
                    newOntime = systemFunction.delayOnTime(ontime, shutdownSetting.offTime)
                    x.onTime = newOntime
                else:
                    x.onTime = systemFunction.nextWeekDayTime(ontime)

            session.commit()

    def initScheduleSetting(self):
        nextWeekDaysDic = systemFunction.getNext7Weekdays()
        now = systemFunction.getDatetimeNonw()

        with DBSession.db_session(settings.PPPE_DB) as session:
            schedule1stQuery = session.query(Schedule).all()

            # 先在第一個loop 更新所有屬性(除了ontime)
            for item in schedule1stQuery:
                offTime = nextWeekDaysDic[item.days].replace(hour=item.offTime.hour,
                                                             minute=item.offTime.minute, second=00,
                                                             microsecond=00)

                item.offTime = systemFunction.nextWeekDayTime(offTime)
                item.updateTime = now

            session.commit()

            schedule2ndQuery = session.query(Schedule).all()
            shutdownSetting = None
            allOffSchedule = list(filter(lambda x: x.offAction, schedule2ndQuery))

            if len(allOffSchedule) > 0:
                shutdownSetting = min(allOffSchedule,
                                      key=attrgetter('offTime'))  # Python min function with a list of objects

            # 在第二個loop更新ontime, 因ontime受offTime影響, 須待offTime先寫入, 才能更新
            for x in schedule2ndQuery:
                ontime = nextWeekDaysDic[x.days].replace(hour=x.onTime.hour,
                                                         minute=x.onTime.minute, second=00, microsecond=00)

                if shutdownSetting is not None:
                    newOntime = systemFunction.delayOnTime(ontime, shutdownSetting.offTime)
                    x.onTime = newOntime
                else:
                    x.onTime = systemFunction.nextWeekDayTime(ontime)

            session.commit()

    def addEnergyConsumption(self, consumption):

        try:
            flag = False
            now = systemFunction.getDatetimeNonw()
            with DBSession.db_session(settings.PPPE_DB) as session:
                data = EnergyConsumption()
                data.consumption = consumption
                data.createTime = now
                session.add(data)
                session.commit()
                flag = True

            return flag
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readEnergySetting(self):
        settingWithoutCost = None
        cost = None
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                settingWithoutCost = session.query(EnergySetting).first()
                cost = session.query(EnergyCost).join(EnergySetting).all()
        except Exception:
            traceback.print_exc(file=sys.stdout)

        return (settingWithoutCost, cost)

    def updateEnergySetting(self, tupleData):
        flag = False
        now = systemFunction.getDatetimeNonw()
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                setting = session.query(EnergySetting).first()

                if setting is not None:
                    updateEnergySetting = tupleData[0]
                    setting.country = updateEnergySetting.country
                    setting.co2EmittedKg = updateEnergySetting.co2EmittedKg
                    setting.co2EmittedLb = updateEnergySetting.co2EmittedLb
                    setting.measurement = updateEnergySetting.measurement
                    setting.updateTime = now

                    session.query(EnergyCost).delete()
                    updateEnergyCostArr = tupleData[1]
                    costArrayTemp = []

                    for index, costTmp in enumerate(updateEnergyCostArr):
                        cost = EnergyCost()
                        cost.cost = costTmp.cost
                        cost.startTime = costTmp.startTime

                        if index + 1 == len(updateEnergyCostArr):
                            cost.endTime = datetime.datetime(1, 1, 1, 0, 0)
                        else:
                            cost.endTime = costTmp.endTime

                        cost.energySettingId = setting.id
                        cost.updateTime = now
                        session.add(cost)
                        costArrayTemp.append(cost)

                session.commit()
                flag = True
                self.energySetting = self.readEnergySetting()

        except Exception:
            traceback.print_exc(file=sys.stdout)

        return flag

    def energyReportQuery(self, startDate, endDate):

        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                startDate = startDate.replace(hour=00, minute=00, second=00)
                endDate = endDate.replace(hour=23, minute=59, second=59)

                allConsumption = session.query(EnergyConsumption).filter(
                    EnergyConsumption.createTime.between(str(startDate), str(endDate))).all()  # 取日期區間內EnergyConsumption, unit: Wh

                cumulativeEnergyConsumption = sum(x.consumption for x in allConsumption)  # 區間內總能耗, unit: Wh

                cumulativeCost = 0  # 區間內總能耗成本,unit: currency by country, 計算: 每段區間能耗(kWh) * 每段區間能耗cost(Cost per kWh) 之加總
                co2Emitted = 0  # 區間內co2排放量,unit: kg or lb, 計算: 區間內總能耗(kWh) * CO₂ Emitted per kWh

                setting = session.query(EnergySetting).first()
                if setting is not None:
                    costList = session.query(EnergyCost).filter(
                        EnergyCost.energySettingId == setting.id).all()  # 取所有cost設定區間

                    for cost in costList:
                        costStartTime = cost.startTime.replace(hour=00, minute=00, second=00)

                        if cost.endTime == datetime.datetime(1, 1, 1, 0, 0):
                            costEndTime = datetime.datetime.now().replace(hour=23, minute=59, second=59)
                        else:
                            costEndTime = cost.endTime.replace(hour=23, minute=59, second=59)

                        costValue = cost.cost  # Cost per kWh

                        consumptionQuery = list(
                            filter(lambda x: x.createTime >= costStartTime and x.createTime <= costEndTime,
                                   allConsumption))

                        cumulativeCost += (costValue * (sum(s.consumption for s in consumptionQuery) / 1000))  # Wh to kWh

                    if len(costList) > 0:
                        if setting.measurement == 0:  # 0表示kg
                            co2Emitted = (cumulativeEnergyConsumption / 1000) * setting.co2EmittedKg  # unit: kg for kWh
                        elif setting.measurement == 1:  # 1表示lb
                            co2Emitted = (cumulativeEnergyConsumption / 1000) * setting.co2EmittedLb  # unit: lb for kWh

                return (round(cumulativeEnergyConsumption, 1), round(cumulativeCost, 2), round(co2Emitted, 3), setting)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readEventEnum(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                return session.query(EventEnum).all()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def queryEventLog(self, startDate, endDate, level, queryStr, limit, paging, currentPageNo, limitId):

        # startDate: 搜尋起始日
        # endDate: 搜尋結束日
        # level: 事件層級
        # queryStr: 搜尋關鍵字
        # limit: Events log每頁最多顯示筆數
        # paging: 分頁flag, True = 有分頁, False = 無分頁

        result = list()
        with DBSession.db_session(settings.PPPE_DB) as session:
            startDate = startDate.replace(hour=0, minute=0, second=0)
            endDate = endDate.replace(hour=23, minute=59, second=59)
            logs = session.query(EventLog).filter(EventLog.CreateTime.between(str(startDate), str(endDate))).order_by(EventLog.id.desc()).all()

            if level is not None and isinstance(level, int):
                if level >= 0:
                    logs = list(filter(lambda x: x.EventId in self.allEventEnum and level == self.allEventEnum[x.EventId].status, logs))
                elif level == -1:  # hardware status
                    logs = list(filter(lambda x: (x.isHwFault is True) and (x.EventId in self.allEventEnum and self.allEventEnum[x.EventId].number != ErrorCodeEventNumber.ID_HARDWARE_STATUS_RESTORE.value), logs))

            if not systemFunction.stringIsNullorEmpty(queryStr):

                locale = appLocaleData.appLocaleRecorder().appLocale # 拿語言
                config = session.query(Configuration).filter(Configuration.IsActive).first()
                if config is not None:
                    locale = config.langSetting

                self.i18nTranslater = i18nTranslater.i18nTranslater(locale)

                tempLogs = list()
                for index, item in enumerate(logs):

                    if item.EventId in self.allEventEnum:
                        key = "eventId_" + str(self.allEventEnum[item.EventId].number)

                        desc = ""
                        if hasattr(i18nId.i18nId(), key):
                            desc = self.i18nTranslater.getTranslateString(getattr(i18nId.i18nId(), key))

                            if item.isHwFault is True:
                                subKey = "eventCode_" + item.errorCode
                                if hasattr(i18nId.i18nId(), subKey):
                                    desc += ":" + item.errorCode + ", " + self.i18nTranslater.getTranslateString(getattr(i18nId.i18nId(), subKey))

                        # item.desc = desc
                        if queryStr.upper() in desc.upper():
                            tempLogs.append(item)

                logs = tempLogs

            pageIndex = dict()  # 事件分頁索引dictionary, {"頁數1":"頁數1最後一筆event id", ... "頁數n":"頁數n最後一筆event id"}
            pageCnt = 0  # 計算頁數
            logsAmount = len(logs)
            conFlag = False  # 決定是否需要在loop中建立索引

            if logsAmount == 0:  # result is empty
                return result, pageIndex

            if logsAmount > 0 and logsAmount < limit:  # 事件總筆數不滿一頁時
                pageIndex[1] = logs[-1].id  # 直接取最後一筆event id, 索引建立完畢
            else:
                conFlag = True

            newLogs = list()
            for index, subItem in enumerate(logs):

                logNo = index + 1
                if conFlag:  # fulfill pagination index
                    remainder = logNo % limit

                    if logNo >= limit: # 事件No.大於等於一頁時
                        if remainder == 0 or logNo == logsAmount:
                            pageCnt += 1 # 頁數n
                            pageIndex[pageCnt] = subItem.id # 頁數n最後一筆event id

                obj = EventObj()
                obj.pid = subItem.id  # id for paging
                obj.id = subItem.EventId
                obj.time = subItem.CreateTime
                if subItem.EventId in self.allEventEnum:
                    # obj.lv = subItem.EventEnum[0].status
                    obj.lv = self.allEventEnum[subItem.EventId].status
                # obj.text = subItem.EventEnum[0].description

                if isinstance(subItem.isHwFault, bool):
                    obj.hwFlag = int(subItem.isHwFault)  # In Python 3.x True and False are keywords and will always be equal to 1 and 0.
                else:
                    obj.hwFlag = subItem.isHwFault

                obj.errCode = subItem.errorCode
                obj.lvCode = subItem.levelCode

                if obj.lvCode is not None:
                    if obj.lvCode in self.allEventLvCodes:
                        obj.clCode = self.allEventLvCodes[obj.lvCode].ColorCode
                    else:
                        obj.clCode = "#777777"  # 沒有任何燈號與顯示

                newLogs.append(obj)

        logsAmount = len(newLogs)

        if paging is False: # 重新搜尋時paging必為False, 頁數要導到最新一頁(第一頁)
            currentPageNo = 1

        lastPageNo = 1  # inital value
        if len(pageIndex) > 0:
            lastPageNo = int(list(pageIndex)[-1])

        isLastPage = (currentPageNo == lastPageNo)
        if currentPageNo in pageIndex:
            limitId = pageIndex[currentPageNo]  # refresh limitId

        if paging is True:
            if isLastPage is True:
                if logsAmount == (lastPageNo * limit):  # = full page qty
                    takeQty = limit
                else:
                    takeQty = logsAmount - ((lastPageNo - 1) * limit)
            else:
                takeQty = limit
        else:
            if logsAmount >= limit:
                takeQty = limit
            else:
                takeQty = logsAmount

        self.lastEventFilter = [startDate, endDate, level, queryStr, limit, paging, currentPageNo, limitId]

        newLogs = list(filter(lambda x: x.pid >= limitId, newLogs))

        if len(newLogs) > takeQty:
            sliceQty = len(newLogs) - takeQty  # determine slice events qty
        else:
            sliceQty = 0
        result = list(islice(newLogs, sliceQty, None))  # remove sliceQty from the list begining

        return result, pageIndex

    def clearEventLogs(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                session.query(EventLog).delete()
                session.commit()
                return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return False

    def updateAppAccount(self, data):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                account = session.query(Account).first()

                if account is not None:
                    account.accountId = data.accountId
                    account.accountSecret = data.accountSecret

                    if data.acode is not None:
                        account.acode = data.acode
                else:
                    session.add(data)

                session.commit()
        except Exception:
            traceback.print_exc(file=sys.stdout)()

    def readAppAccount(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                account = session.query(Account).first()
                return account
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def addDeviceLog(self, data):  # data type: DeviceLog

        try:
            flag = False
            now = datetime.datetime.now()
            unix_ts = int(now.timestamp())
            local_time = now
            with DBSession.db_session(settings.PPPE_DB) as session:
                data.LocalTime = local_time
                data.ts = unix_ts
                session.add(data)
                session.commit()
                flag = True

            return flag, now
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def deviceLogQuery(self, startDate, endDate, dcode):

        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                logs = session.query(DeviceLog).filter(DeviceLog.dcode == dcode).filter(DeviceLog.LocalTime.between(str(startDate), str(endDate))).all()

                return logs
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readAllEventCode(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                temp = session.query(HardwareFaultCodeInfo).all()

                result = dict()
                for k,v in enumerate(temp):
                    result[v.ErrorCode] = v

                return result

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readAllEventLevelCode(self):
        try:
            with DBSession.db_session(settings.PPPE_DB) as session:
                temp = session.query(HardwareFaultLevelInfo).all()

                result = dict()
                for k,v in enumerate(temp):
                    result[v.LevelCode] = v

                return result

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readAllEventEnum(self):
        try:
            temp = self.readEventEnum()

            result = dict()
            for k,v in enumerate(temp):
                result[v.number] = v

            return result

        except Exception:
            traceback.print_exc(file=sys.stdout)

class EmailServiceProvider(Enum):
    GMAIL = 0
    OTHER = 1

class EventObj(object):

    def __init__(self, jsonString = None):
        self._id = None
        self._time = None
        self._lv = None
        self._text = None
        self._hwFlag = None
        self._errCode = None
        self._lvCode = None
        self._clCode = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def toJson(self):
        try:
            json_string = ""
            s1 = ""
            for attr, value in self.__dict__.items():

                if not systemFunction.stringIsNullorEmpty(attr):
                    attr = attr.replace("_", "")
                    if value is None:
                        # s1 += '"{}":{},'.format(attr, "null")
                        pass

                    if isinstance(value, (int, float)):
                        s1 += '"{}":{},'.format(attr, str(value))

                    if isinstance(value, str):
                        s1 += '"{}":"{}",'.format(attr, value)

                    if isinstance(value, datetime.datetime):
                        value = value.isoformat().replace("T", " ")
                        s1 += '"{}":"{}",'.format(attr, value)

            if s1 != "":
                s1 = s1[:-1]  # Remove final character
                json_string += "{" + s1 + "},"

            json_string = json_string[:-1]  # Remove final character

            return json_string
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return "{}"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def lv(self):
        return self._lv

    @lv.setter
    def lv(self, value):
        self._lv = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def hwFlag(self):
        return self._hwFlag

    @hwFlag.setter
    def hwFlag(self, value):
        self._hwFlag = value

    @property
    def errCode(self):
        return self._errCode

    @errCode.setter
    def errCode(self, value):
        self._errCode = value

    @property
    def lvCode(self):
        return self._lvCode

    @lvCode.setter
    def lvCode(self, value):
        self._lvCode = value

    @property
    def clCode(self):
        return self._clCode

    @clCode.setter
    def clCode(self, value):
        self._clCode = value


# import json
# import traceback
# import sys
# import requests
# from System import systemFunction, systemDefine
# from datetime import datetime, timedelta


# now = datetime(2020, 3, 20, 17, 21, 27, 279190)
# startDate = now - timedelta(days=3)
# endDate = now
#
# db = DataSource2()
# z = db.readEventEnum()
# logs = db.queryEventLog(startDate, endDate, -1, "c51")
# # resp = json.dumps(logs, default=systemFunction.jsonSerialize)
# json_string = json.dumps([item.toJson() for item in logs])

# db = DataSource2()
# z = db.readAllEventCode()
# pass
