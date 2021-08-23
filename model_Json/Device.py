from model_Json import DeviceStatusData, DevicePropertiesData, DataSource2, DevicePushMessageData, WebAppData
from views.Custom import ViewData
from controllers import DeviceConfigure, DevicePropertiesFetcher
import traceback
from controllers import DesktopInteractiveServer, BypassEventCount
from i18n import appLocaleData
from System import systemFunction, systemDefine, loggerSetting
from Utility import Scheduler


class Device:
    def __init__(self):
        try:
            self._deviceStatus = DeviceStatusData.DeviceStatus()
            self._dataSource = DataSource2.DataSource2()
            self._deviceConfigure = DeviceConfigure.DeviceConfigure()
            self._deviceId = -1
            self._devicePropData = DevicePropertiesData.DevicePropertiesData()
            self._propertyFetcher = DevicePropertiesFetcher.DeviceProperties(self._devicePropData)
            self._viewData = ViewData

            self.cumEnergyConsumptionMonitor = float(0)
            self._propertyFetcher.propertySignal.connect(self._devicePropData.updatePropertiesSignal)
            self._propertyFetcher.noFetchSignal.connect(self._devicePropData.disableConfigureSlot)
            self._desktopInteractiveServer = DesktopInteractiveServer.DesktopInteractiveServer()
            self._schedulerManager = Scheduler.SchedulerManager(self._desktopInteractiveServer)

            self.summaryFilter = 1

            # PPP mobile solution"
            self.mobileSolutionEnable = False
            self.mobileLoginState = False
            self.topicId = None
            self._isLostCommunication = True
            self._customUPSName = None
            self._upsSN_Temp = None  # 暫存UPS SN: 換機器時, 可取得上一台UPS SN
            self._freqConstant = systemDefine.DEVICE_STATUS_MESSAGE_INTERVAL
            self._freqAppAct = systemDefine.APNS_SILENCE_MESSAGE_INTERVAL
            self._devicePushSilenceMsg = DevicePushMessageData.SilenceMessage()
            self._devicePushAlertMsg = DevicePushMessageData.AlertMessage()
            self._mobileLoginItem = WebAppData.AccountMobileLoginItem()
            self._updateDeviceParam = WebAppData.UpdateDeviceParam()
            self._checkDuplicateDeviceParam = WebAppData.CheckDuplicateDeviceParam()
            self._APNsLostCommunicationMsgTimesLimit = (systemDefine.APNS_LOST_COMMUNICATION_SILENCE_MESSAGE_SEND_DURATION/systemDefine.APNS_SILENCE_MESSAGE_INTERVAL) # send APNS msg times limit
            self._EmqLostCommunicationMsgTimesLimit = (systemDefine.EMQ_LOST_COMMUNICATION_MESSAGE_SEND_DURATION/systemDefine.DEVICE_STATUS_MESSAGE_INTERVAL)  # send EMQ msg times limit
            self._APNsLostCommunicationMsgCount = 0  # send APNS msg count
            self._EmqLostCommunicationMsgCount = 0  # send EMQ msg count
            self._ResendEmqMsgCount = 0  # re-send EMQ status msg count
            self._ProcessorId = None
            self._SMBiosUUID = None
            self._acode = None  # account id
            self._isNoneSN = False  # 判斷是否None SN
            self._altSN = None  # 判斷是否None SN
            self._otpKey = None  # one time pass

            # cloud events
            self._eventEnum = self._dataSource.readEventEnum()  # Power Panel Cloud all events, read only!!!
            self._dcode = None  # device id
            self._cloudEvents = []  # emq message event content
            self._eventStatData = []  # statement data, like "FaultCode"
            self._cloudEvtDisplay = []  # cloud event display flag
            self._cloudEvtSend = []  # cloud event data send flag
            self._cloudEvtDur = 30  # send cloud event log duration, unit:second
            self._bypassEventCount = BypassEventCount.BypassEventCount()  # bypass event counter
            self._enterHibernation = False
            self._cloudEventId = self.eventEnumInit()
            self._cloudEventsTemp = []  # emq message event content

            # battery test
            self._btestTs = None  # UNIX  epoch time, for check battery test request packet
            self._cloudBtestFlag = False
            self._cloudBtestResult = None

            # 設定Daemon的語系預設值(from DB)
            if systemFunction.stringIsNullorEmpty(self._dataSource.configurationSetting.langSetting) == False:
                appLocaleData.appLocaleRecorderFromDB().appLocale = self._dataSource.configurationSetting.langSetting

        except Exception:
            raise
            import sys
            traceback.print_exc(file=sys.stdout)


    def restoreData(self):
        self._dataSource.restore()

    def eventEnumInit(self):
        member_list = list(map(lambda x: x.reasoning, self._eventEnum))
        return systemFunction.listToEnum(member_list, "CloudEvent", 0)

    @property
    def freqConstant(self):
        return self._freqConstant

    @freqConstant.setter
    def freqConstant(self, value):
        self._freqConstant = value

    @property
    def freqAppAct(self):
        return self._freqAppAct

    @freqAppAct.setter
    def freqAppAct(self, value):
        self._freqAppAct = value

    @property
    def customUPSName(self):
        return self._customUPSName

    @customUPSName.setter
    def customUPSName(self, value):
        self._customUPSName = value

    @property
    def desktopInteractiveServer(self):
        return self._desktopInteractiveServer

    @desktopInteractiveServer.setter
    def desktopInteractiveServer(self, value):
        self._desktopInteractiveServer = value

    @property
    def devicePropData(self):
        return self._devicePropData

    @devicePropData.setter
    def devicePropData(self, value):
        self._devicePropData = value

    @property
    def propertyFetcher(self):
        return self._propertyFetcher

    @propertyFetcher.setter
    def propertyFetcher(self, value):
        self._propertyFetcher = value

    @property
    def deviceId(self):
        return self._deviceId

    @deviceId.setter
    def deviceId(self, value):
        self._deviceId = value

    @property
    def deviceConfigure(self):
        return self._deviceConfigure

    @deviceConfigure.setter
    def deviceConfigure(self, value):
        self._deviceConfigure = value

    @property
    def dataSource(self):
        return self._dataSource

    @dataSource.setter
    def dataSource(self, value):
        self._dataSource = value

    @property
    def deviceStatus(self):
        return self._deviceStatus

    @deviceStatus.setter
    def deviceStatus(self, value):
        self._deviceStatus = value

    @property
    def devicePushSilenceMsg(self):
        return self._devicePushSilenceMsg

    @devicePushSilenceMsg.setter
    def devicePushSilenceMsg(self, value):
        self._devicePushSilenceMsg = value

    @property
    def devicePushAlertMsg(self):
        return self._devicePushAlertMsg

    @devicePushAlertMsg.setter
    def devicePushAlertMsg(self, value):
        self._devicePushAlertMsg = value

    @property
    def mobileLoginItem(self):
        return self._mobileLoginItem

    @mobileLoginItem.setter
    def mobileLoginItem(self, value):
        self._mobileLoginItem = value

    @property
    def updateDeviceParam(self):
        return self._updateDeviceParam

    @updateDeviceParam.setter
    def updateDeviceParam(self, value):
        self._updateDeviceParam = value

    @property
    def checkDuplicateDeviceParam(self):
        return self._checkDuplicateDeviceParam

    @checkDuplicateDeviceParam.setter
    def checkDuplicateDeviceParam(self, value):
        self._checkDuplicateDeviceParam = value

    @property
    def isLostCommunication(self):
        return self._isLostCommunication

    @isLostCommunication.setter
    def isLostCommunication(self, value):
        self._isLostCommunication = value

    @property
    def APNsLostCommunicationMsgTimesLimit(self):
        return self._APNsLostCommunicationMsgTimesLimit

    @APNsLostCommunicationMsgTimesLimit.setter
    def APNsLostCommunicationMsgTimesLimit(self, value):
        self._APNsLostCommunicationMsgTimesLimit = value

    @property
    def EmqLostCommunicationMsgTimesLimit(self):
        return self._EmqLostCommunicationMsgTimesLimit

    @EmqLostCommunicationMsgTimesLimit.setter
    def EmqLostCommunicationMsgTimesLimit(self, value):
        self._EmqLostCommunicationMsgTimesLimit = value

    @property
    def APNsLostCommunicationMsgCount(self):
        return self._APNsLostCommunicationMsgCount

    @APNsLostCommunicationMsgCount.setter
    def APNsLostCommunicationMsgCount(self, value):
        self._APNsLostCommunicationMsgCount = value

    @property
    def EmqLostCommunicationMsgCount(self):
        return self._EmqLostCommunicationMsgCount

    @EmqLostCommunicationMsgCount.setter
    def EmqLostCommunicationMsgCount(self, value):
        self._EmqLostCommunicationMsgCount = value

    @property
    def ResendEmqMsgCount(self):
        return self._ResendEmqMsgCount

    @ResendEmqMsgCount.setter
    def ResendEmqMsgCount(self, value):
        self._ResendEmqMsgCount = value

    @property
    def acode(self):
        return self._acode

    @acode.setter
    def acode(self, value):
        self._acode = value

    @property
    def ProcessorId(self):
        return self._ProcessorId

    @ProcessorId.setter
    def ProcessorId(self, value):
        self._ProcessorId = value

    @property
    def SMBiosUUID(self):
        return self._SMBiosUUID

    @SMBiosUUID.setter
    def SMBiosUUID(self, value):
        self._SMBiosUUID = value

    @property
    def isNoneSN(self):
        return self._isNoneSN

    @isNoneSN.setter
    def isNoneSN(self, value):
        self._isNoneSN = value

    @property
    def altSN(self):
        return self._altSN

    @altSN.setter
    def altSN(self, value):
        self._altSN = value

    @property
    def upsSN_Temp(self):
        return self._upsSN_Temp

    @upsSN_Temp.setter
    def upsSN_Temp(self, value):
        self._upsSN_Temp = value

    @property
    def eventEnum(self):
        return self._eventEnum

    @eventEnum.setter
    def eventEnum(self, value):
        self._eventEnum = value

    @property
    def dcode(self):
        return self._dcode

    @dcode.setter
    def dcode(self, value):
        self._dcode = value

    @property
    def cloudEvents(self):
        return self._cloudEvents

    @cloudEvents.setter
    def cloudEvents(self, value):
        self._cloudEvents = value

    @property
    def cloudEvtDisplay(self):
        return self._cloudEvtDisplay

    @cloudEvtDisplay.setter
    def cloudEvtDisplay(self, value):
        self._cloudEvtDisplay = value

    @property
    def cloudEvtSend(self):
        return self._cloudEvtSend

    @cloudEvtSend.setter
    def cloudEvtSend(self, value):
        self._cloudEvtSend = value

    @property
    def cloudEvtDur(self):
        return self._cloudEvtDur

    @cloudEvtDur.setter
    def cloudEvtDur(self, value):
        self._cloudEvtDur = value

    @property
    def bypassEventCount(self):
        return self._bypassEventCount

    @bypassEventCount.setter
    def bypassEventCount(self, value):
        self._bypassEventCount = value

    @property
    def enterHibernation(self):
        return self._enterHibernation

    @enterHibernation.setter
    def enterHibernation(self, value):
        self._enterHibernation = value

    @property
    def cloudEventId(self):
        return self._cloudEventId

    @cloudEventId.setter
    def cloudEventId(self, value):
        self._cloudEventId = value

    @property
    def eventStatData(self):
        return self._eventStatData

    @eventStatData.setter
    def eventStatData(self, value):
        self._eventStatData = value

    @property
    def cloudEventsTemp(self):
        return self._cloudEventsTemp

    @cloudEventsTemp.setter
    def cloudEventsTemp(self, value):
        self._cloudEventsTemp = value

    @property
    def schedulerManager(self):
        return self._schedulerManager

    @schedulerManager.setter
    def schedulerManager(self, value):
        self._schedulerManager = value

    @property
    def btestTs(self):
        return self._btestTs

    @btestTs.setter
    def btestTs(self, value):
        self._btestTs = value

    @property
    def cloudBtestFlag(self):
        return self._cloudBtestFlag

    @cloudBtestFlag.setter
    def cloudBtestFlag(self, value):
        self._cloudBtestFlag = value

    @property
    def cloudBtestResult(self):
        return self._cloudBtestResult

    @cloudBtestResult.setter
    def cloudBtestResult(self, value):
        self._cloudBtestResult = value

    @property
    def otpKey(self):
        return self._otpKey

    @otpKey.setter
    def otpKey(self, value):
        self._otpKey = value
