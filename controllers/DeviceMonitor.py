import sys
import traceback
import model_Json.DeviceStatusData

from PyQt5.QtCore import QObject, QTimer
import time
from System import systemDefine as sysDef, systemFunction, ValueId
from controllers import EventAnalyzer, EnergyRecorder, MobileDataProvider, DeviceLogHelper, TransactionHelper, WebAppController
from model_Json import DeviceStatusData, DevicePushMessageData, Transaction, Statement
from model_Json.tables.Configuration import Configuration
from Utility import Logger
from views.Custom.ViewData import EventCodeLevelStatus


# DeviceMonitor只有開機時會init一次
class DeviceMonitor(QObject):
    def __init__(self, server ,device):
        super(DeviceMonitor, self).__init__()
        self.EventID = device.cloudEventId
        self.transactionData = Transaction.Transaction()
        self.helper = TransactionHelper.TransactionHelper()
        self.deviceId = self.lookupPresentDeviceId()
        self.propertyFetcher = device.propertyFetcher
        self.deviceConfigure = device.deviceConfigure
        self.eventAnalyzer = EventAnalyzer.EventAnalyzer(server, device)
        self.energyRecorder = EnergyRecorder.EnergyRecorder(device, self.helper)
        self.deviceStatus = device.deviceStatus
        self.device = device
        self.configChangeId = 0
        self.configChangeSyncId = 0
        self.isLostCommunication = True

        self.isSelfTestFWErrorCount = 0
        self.isSelfTestFWErrorFlag = False
        self.shouldUpdateDeviceId = False
        self.isSelfTestFailFlag = False  # 當battery test指令成功下給UPS, 但UPS回傳ERR code != 0時flag為T

        # PPP mobile solution"
        self.FcmMsgProvider = MobileDataProvider.FcmMsgProvider(device)
        self.EmqMsgProvider = MobileDataProvider.EmqMsgProvider(device)
        self.DeviceLogHelper = DeviceLogHelper.DevLogHelper(device)
        self.WebAppController = WebAppController.WebAppController(device)

        # status flag
        self.batteryTesting = False
        self.isRetry = False

        # cloud events
        self.event_number_dict = {}
        self.eventDictInit()

        self.cloudBatteryTesting = False

        try:

            if self.deviceId != -1:
                self.propertyFetcher.fetchAllProperties(self.helper, self.deviceId)  # device properties只有開機時會取一次
                self.device.customUPSName = self.device.devicePropData.modelName.value  # custom UPS name給預設值
                self.device.upsSN_Temp = self.device.devicePropData.serialNumber.value  # upsSN_Temp給預設值
                self.device.bypassEventCount.reset()  # clear bypass event counter
                self.device.enterHibernation = False

                Logger.LogIns().logger.info("***[Monitor]DeviceMonitor init device SN: " + str(self.device.devicePropData.serialNumber.value) + "***")
                Logger.LogIns().logger.info("***[Monitor]DeviceMonitor init upsSN_Temp: " + str(self.device.upsSN_Temp) + "***")

                self.energyRecorder.energyConsumptionScheduler()

            # 取config設定值與機器是否連線無關
            self.deviceConfigure.fetchAllConfig()
            self.FcmMsgProvider.setDeviceConfigToSilenceMsg()

            self.timer = QTimer()
            self.timer.timeout.connect(self.monitoring)
            self.timer.start(sysDef.DEVICE_MONITOR_INTERVAL * 1000) # msecs

        except Exception as e:
            Logger.LogIns().logger.error("Monitor Error")
            Logger.LogIns().logger.error(traceback.format_exc())

    def monitoring(self):
        try:
            """deviceId == -1: find UPS ;else fetch device status"""
            Logger.LogIns().logger.info("***[Monitor]into monitoring deviceId chk1: " + str(self.deviceId) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeId: " + str(self.configChangeId) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeSyncId: " + str(self.configChangeSyncId) + "***")

            if self.deviceId == -1:
                trx = Transaction.Transaction()
                trx.deviceId = -1

                self.deviceStatus.deviceId = -1
                self.device.deviceId = -1
                self.deviceId = self.lookupPresentDeviceId()

                # Logger.LogIns().logger.info("***[Monitor]into monitoring deviceId chk2: " + str(self.deviceId) + "***")
                Logger.LogIns().logger.info("***[Monitor]into monitoring isLostCommunication chk2: " + str(self.device.isLostCommunication) + "***")

                if self.deviceId != -1:
                    Logger.LogIns().logger.info("***[Monitor]into monitoring deviceId chk3: " + str(self.deviceId) + "***")
                    self.device.deviceId = self.deviceId

                    flag = self.fetchStatusData(self.helper, self.deviceId)

                    Logger.LogIns().logger.info("***[Monitor]into monitoring fetchStatusData: " + str(flag) + "***")

                    # 取prop
                    self.propertyFetcher.fetchAllProperties(self.helper, self.deviceId)  # device properties只有開機時會取一次
                    self.device.customUPSName = self.device.devicePropData.modelName.value  # custom UPS name給預設值
                    self.device.upsSN_Temp = self.device.devicePropData.serialNumber.value  # upsSN_Temp給預設值
                    self.device.bypassEventCount.reset()  # clear bypass event counter
                    self.device.enterHibernation = False

                    Logger.LogIns().logger.info("***[Monitor]into monitoring device SN-1: " + str(self.device.devicePropData.serialNumber.value) + "***")
                    Logger.LogIns().logger.info("***[Monitor]into monitoring altSN-1: " + str(self.device.altSN) + "***")

                    # start energy consumption
                    self.energyRecorder.energyConsumptionScheduler()
                    # self.propertyFetcher.sendEmqStatusMsgSignal.emit(0)

                    Logger.LogIns().logger.info("***[Monitor]into monitoring device SN-2: " + str(self.device.devicePropData.serialNumber.value) + "***")
                    Logger.LogIns().logger.info("***[Monitor]into monitoring altSN-2: " + str(self.device.altSN) + "***")

                    self.saveAndSendDeviceLog()

                    if not flag:
                        self.deviceId = -1
                        self.transactionData.deviceId = -1
            elif self.deviceId != -1:
                Logger.LogIns().logger.info("***[Monitor]into monitoring deviceId chk4: " + str(self.deviceId) + "***")
                Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeId chk4-1: " + str(self.configChangeId) + "***")
                Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeSyncId chk4-1: " + str(self.configChangeSyncId) + "***")

                if self.isUnexpectedDisconnect():
                    self.configChangeSyncId = 0
                    self.configChangeId = 0
                    self.shouldUpdateDeviceId = True

                else:
                    if self.shouldUpdateDeviceId == True:
                        presentDeviceId = self.lookupPresentDeviceId()
                        if presentDeviceId != -1:
                            self.deviceId = presentDeviceId
                        self.shouldUpdateDeviceId = False

                    flag = self.fetchStatusData(self.helper, self.deviceId)

                    Logger.LogIns().logger.info("***[Monitor]into monitoring fetchStatus: " + str(flag) + "***")
                    Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeId chk4-2: " + str(self.configChangeId) + "***")
                    Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeSyncId chk4-2: " + str(self.configChangeSyncId) + "***")

                    if flag:
                        self.isRetry = False
                        self.deviceStatus.deviceId = self.deviceId
                        self.device.deviceId = self.deviceId
                    # if not self.isUnexpectedDisconnect(self.device.devicePropData.modelName.value):
                    if not self.isUnexpectedDisconnect():

                        # if not flag and not self.isUnexpectedDisconnect(self.device.devicePropData.modelName.value):  # recheck device is reconnecting or not
                        if not flag and not self.isUnexpectedDisconnect():
                            if self.device.enterHibernation:
                                self.device.bypassEventCount.reset()  # clear bypass event counter

                            if self.deviceStatus.InputStatus == DeviceStatusData.InputStatus.Normal.value:
                                if not self.isLostCommunication:
                                    self.isLostCommunication = True
                                    self.device.isLostCommunication = True
                                    self.eventAnalyzer.occur(eventId=self.EventID.ID_COMMUNICATION_LOST)
                            else:
                                self.eventAnalyzer.occurOnece(self.EventID.ID_LOCAL_COMMUNICATION_LOST_IN_BATTERY)

                    if flag and self.isLostCommunication:  # restored from communication lost
                        Logger.LogIns().logger.info("***[Monitor]into monitoring condition1***")

                        self.isLostCommunication = False
                        self.device.isLostCommunication = False
                        self.device.APNsLostCommunicationMsgCount = 0
                        self.device.EmqLostCommunicationMsgCount = 0
                        self.eventAnalyzer.restoreOccur(eventId=self.EventID.ID_COMMUNICATION_ESTABLISHED)
                    if self.configChangeId > self.configChangeSyncId and self.isUnexpectedDisconnect() is not True:  # 同步面板與機器設定值
                        Logger.LogIns().logger.info("***[Monitor]into monitoring condition2***")
                        Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeId2-1: " + str(self.configChangeId) + "***")
                        Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeSyncId2-1: " + str(self.configChangeSyncId) + "***")

                        self.propertyFetcher.updateProperties(self.helper, self.deviceId, self.configChangeId)
                        self.propertyFetcher.fetchChangedProperties(self.helper, self.deviceId)
                        self.configChangeSyncId = self.configChangeId

                        Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeId2-2: " + str(self.configChangeId) + "***")
                        Logger.LogIns().logger.info("***[Monitor]into monitoring configChangeSyncId2-2: " + str(self.configChangeSyncId) + "***")
                        Logger.LogIns().logger.info("***[Monitor]into monitoring device SN: " + str(self.device.devicePropData.serialNumber.value) + "***")
                        Logger.LogIns().logger.info("***[Monitor]into monitoring altSN: " + str(self.device.altSN) + "***")
                    if not flag:
                        Logger.LogIns().logger.info("***[Monitor]into monitoring condition3***")

                        if not self.isRetry:
                            Logger.LogIns().logger.info("query status failed Retry once")
                            self.isRetry = True
                            self.configChangeSyncId = 0
                            self.configChangeId = 0
                            self.shouldUpdateDeviceId = True
                        else:
                            Logger.LogIns().logger.info("Lost Communication")
                            self.isRetry = False
                            self.deviceId = -1
                            self.transactionData.deviceId = -1

                            if self.device.enterHibernation:
                                self.device.bypassEventCount.reset()  # clear bypass event counter
                                self.device.enterHibernation = False

                            # device lost stop energy record
                            self.energyRecorder.stopEnergyConsumptionTimer()
                    if self.deviceId == -1:
                        if not self.isLostCommunication:
                            self.isLostCommunication = True
                            self.device.isLostCommunication = True
                            self.eventAnalyzer.occur(eventId=self.EventID.ID_COMMUNICATION_LOST)
                            self.configChangeSyncId = 0
                            self.configChangeId = 0

                Logger.LogIns().logger.info("***[Monitor]mobileLoginState: " + str(self.device.mobileLoginState) + "***")
                if self.device.mobileLoginState is True:
                    if self.EmqMsgProvider.sendStatusMsgTimer is None:
                        Logger.LogIns().logger.info("***[Monitor] INIT SEND EMQ STATUS***")
                        self.EmqMsgProvider.sendEmqStatusMsg(True)

                self.saveAndSendDeviceLog()

            Logger.LogIns().logger.info("***[Monitor]into monitoring final configChangeId: " + str(self.configChangeId) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final configChangeSyncId: " + str(self.configChangeSyncId) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final device SN: " + str(self.device.devicePropData.serialNumber.value) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final altSN: " + str(self.device.altSN) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final upsSN_Temp: " + str(self.device.upsSN_Temp) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final acode: " + str(self.device.acode) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final isNoneSN: " + str(self.device.isNoneSN) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final customUPSName: " + str(self.device.customUPSName) + "***")
            Logger.LogIns().logger.info("***[Monitor]into monitoring final modelName: " + str(self.device.devicePropData.modelName.value) + "***")

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    """取得DeviceId"""

    def dohibernate(self):
        try:
            self.device.enterHibernation = True
            self.eventAnalyzer.occur(eventId=self.EventID.ID_COMMUNICATION_LOST)
            self.WebAppController.saveAndSendDeviceLog(False)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def dohibernateResume(self):
        try:
            if self.device.enterHibernation is True:
                self.device.cloudEvents.append(self.EventID.ID_COMMUNICATION_ESTABLISHED.value)  # reset UPS status to normal
                self.WebAppController.saveAndSendDeviceLog(False)
                self.device.enterHibernation = False
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
            
    def isUnexpectedDisconnect(self):
        trx = Transaction.Transaction()
        # trx.setDeviceId(self.deviceId)
        stat = Statement.Statement(ValueId.ValueIdFinder().getValueId("UNEXPECTED_DISCONNECT"))

        trx.add(stat)

        flag = self.helper.submit(trx)

        Logger.LogIns().logger.info("***[Monitor]isUnexpectedDisconnect flag: " + str(flag) + "***")
        Logger.LogIns().logger.info("***[Monitor]isUnexpectedDisconnect errCode: " + str(stat.errCode) + "***")
        Logger.LogIns().logger.info("***[Monitor]isUnexpectedDisconnect hasResults: " + str(stat.hasResults) + "***")

        if stat.errCode == 0 and stat.hasResults:
            Logger.LogIns().logger.info("***[Monitor]isUnexpectedDisconnect stat.results[0]: " + str(stat.results[0]) + "***")
            return int(stat.results[0]) == 1
        else:
            return False

    def lookupPresentDeviceId(self):
        deviceId = -1
        trx = Transaction.Transaction()
        # trx = self.transactionData
        stat = Statement.Statement(ValueId.ValueIdFinder().getValueId("LIST_DEVICES"))
        trx.add(stat)
        Logger.LogIns().logger.info("Service.lookupPresentDeviceId: before submit")
        flag = self.helper.submit(trx)
        Logger.LogIns().logger.info("Service.lookupPresentDeviceId: after submit")

        if flag == False:
            Logger.LogIns().logger.warning("Service.lookupPresentDeviceId: submit fail")
            return deviceId

        if trx.state != model_Json.DeviceStatusData.DeviceState.PROXY_STATE_NORMAL.value:
            Logger.LogIns().logger.warning("transaction.state() != DeviceState.PROXY_STATE_NORMAL")
            return deviceId

        if stat.errCode != model_Json.DeviceStatusData.ErrorCode.DRVERR_CMD_NOT_SUPPORT.value and stat.errCode != model_Json.DeviceStatusData.ErrorCode.DRVERR_SUCCESS.value:
            Logger.LogIns().logger.warning("listDeviceStatement.errCode() != ErrorCode.DRVERR_SUCCESS")
            return deviceId

        if stat.hasResults:
            deviceId = int(stat.results[0])
        else:
            Logger.LogIns().logger.warning("! listDeviceStatement.hasResults()")
            return deviceId

        if deviceId == -1:
            Logger.LogIns().logger.warning("Service.lookupPresentDeviceId: no device available.")

        return deviceId

    def fetchStatusData(self, helper, deviceId):
        flag = self.fetchDeviceStatus(helper, deviceId)

        if flag:
            self.device.cloudEvents = []  # CLEAR LIST
            self.device.eventStatData = []  # CLEAR LIST
            self.isSelfTestFailFlag = False  # CLEAR

            deviceStatus = self.getDeviceStatus(self.transactionData)
            if deviceStatus is None:
                return False
            # testResultStatment = self.transactionData.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_TEST_RESULT")]
            # self.printLog(testResultStatment, "STATUS_TEST_RESULT")
            # testResult = testResultStatment is not None and testResultStatment.hasResults

            testResultStatment = None
            if ValueId.ValueIdFinder().getValueId("STATUS_TEST_RESULT") in self.transactionData.statementsDic:
                testResultStatment = self.transactionData.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_TEST_RESULT")]

            self.printLog(testResultStatment, "STATUS_TEST_RESULT")
            testResult = testResultStatment is not None and testResultStatment.hasResults

            # counter energy consumption
            if deviceStatus.LoadWatt:
                self.device.cumEnergyConsumptionMonitor += deviceStatus.LoadWatt  # unit: watts

            if testResult is not None and testResult:
                deviceStatus = self.decideSelfTest(deviceStatus, testResultStatment.results[0])
            else:
                deviceStatus = self.decideSelfTest(deviceStatus)

            # SelfTestFWErrFlag
            if deviceStatus.UtilityPowerFailure == True and deviceStatus.BatteryTesting == True:
                self.isSelfTestFWErrorFlag = True
            elif deviceStatus.UtilityPowerFailure == False and deviceStatus.BatteryTesting == False:
                self.isSelfTestFWErrorFlag = False
                self.isSelfTestFWErrorCount = 0

            if self.isSelfTestFWErrorFlag == True:
                if deviceStatus.UtilityPowerFailure == True and deviceStatus.BatteryTesting == False:
                    self.isSelfTestFWErrorCount += 1
                deviceStatus.SelfTestFWErrFlag = self.isSelfTestFWErrorCount >= 3
            else:
                deviceStatus.SelfTestFWErrFlag = True

            self.deviceStatus.assignDeviceStatus(deviceStatus)  # Personal event only
            self.setDeviceStatusToSilenceMsg(deviceStatus)

            # event handle
            self.eventAnalyzer.analyze(deviceStatus, self.transactionData)
        elif not flag and not self.isRetry:
            return flag
        else:
            self.deviceId = -1
            Logger.LogIns().logger.error("Fetch device status error.")

        return flag

    def saveAndSendDeviceLog(self):
        self.WebAppController.saveAndSendDeviceLog(True)
        if len(self.device.cloudEvents.copy()) > 0:
            Logger.LogIns().logger.info("saveAndSendDeviceLog, occur events {0}".format(str(self.device.cloudEvents.copy())))

            # satisfy conditions:  mobile solution enable, login success.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True:
                self.EmqMsgProvider.restart_send_status_after_event()

    # unexpected disconnect condition:
    # 1. OL/OR series connect via Usb sometimes will lost for a while, in fact, it doesn't lost connection
    # when device is in unexpected disconnect condition, we will let it reconnect once,then decide occur lost communication or not
    # def isUnexpectedDisconnect(self, modelName):
    #     valueIdFinder = ValueId.ValueIdFinder()
    #
    #     if (modelName.startswith("OL") and (len(modelName) > 2 and isinstance(modelName[2], int))) or (modelName is not None and (modelName.upper() == "OR750PFCLCD" or modelName.upper() == "OR1000PFCLCD" or modelName.upper() == "OR1500PFCLCD")):
    #
    #         trx = Transaction.Transaction()
    #         unexpectedDisconnectStatement = Statement.Statement(valueIdFinder.getValueId("UNEXPECTED_DISCONNECT"))
    #         trx.add(unexpectedDisconnectStatement)
    #
    #         flag = self.helper.submit(trx)  # Get transaction from device
    #
    #         if (not flag) or (trx.state != model_Json.DeviceStatusData.DeviceState.PROXY_STATE_NORMAL.value):
    #             return False
    #
    #         unexpectedDisconnectStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("UNEXPECTED_DISCONNECT")]
    #         if unexpectedDisconnectStatement is not None and unexpectedDisconnectStatement.hasResults:
    #             b = unexpectedDisconnectStatement.results[0] == str(1)
    #             return b
    #         else:
    #             return False
    #     else:
    #         return False

    def decideTestResult(self, testResult):
        if testResult == sysDef.TestResult.TEST_PASSED or testResult == sysDef.TestResult.TEST_NOTHING:
            return True
        else:
            return False

    def decideSelfTest(self, deviceStatus, testResult=None):

        # check result if need
        # monitor status is testing and next fetch status is not testing means done

        Logger.LogIns().logger.info("decideSelfTest batteryTesting: " + str(self.batteryTesting))
        Logger.LogIns().logger.info("decideSelfTest status batteryTesting: " + str(deviceStatus.BatteryTesting))
        Logger.LogIns().logger.info("decideSelfTest cloudBtestFlag: " + str(self.device.cloudBtestFlag))

        ispassed = None  # ispassed表示self-test通過與否, t為通過
        if self.batteryTesting:  # previous fetch status is self testing

            Logger.LogIns().logger.info("decideSelfTest into #1")

            batTDateTemp = None
            batTResTemp = None
            continueFlag = False
            if deviceStatus.BatteryTesting is None:  # now fetch self testing status failed

                Logger.LogIns().logger.info("decideSelfTest into #2")
                if self.isSelfTestFailFlag: # 當battery test指令成功下給UPS, 但UPS回傳ERR code != 0時flag為T
                    Logger.LogIns().logger.info("decideSelfTest into #3")
                    ispassed = False
                    config = Configuration()
                    config.selfTestResult = ispassed
                    batTDateTemp = self.device.dataSource.updateDeviceConfig(config)
                    self.batteryTesting = False
                    self.eventAnalyzer.occurOnece(self.EventID.ID_BATTERY_TEST_FAIL)

                    batTResTemp = sysDef.CloudBatteryTestResult.NeverBeExecuted
                    continueFlag = True

            else:  # now fetch self testing status success
                if not deviceStatus.BatteryTesting:  # now fetch status is not self testing
                    Logger.LogIns().logger.info("decideSelfTest into #4")
                    ispassed = True

                    if deviceStatus.HardwareFault is not None and deviceStatus.HardwareFault is True:
                        ispassed = False

                    if testResult is not None:
                        try:
                            Logger.LogIns().logger.info("decideSelfTest into #5")
                            ispassed = self.decideTestResult(int(testResult))
                            config = Configuration()
                            config.selfTestResult = ispassed
                            batTDateTemp = self.device.dataSource.updateDeviceConfig(config)

                            self.batteryTesting = False

                            if ispassed:
                                event = self.decideTestEvent(int(testResult), sysDef.TestResultType.TEST_RESULT, sysDef.TestType.TEST_TYPE_TEST)
                                if event is not None:
                                    batTResTemp = sysDef.CloudBatteryTestResult.Passed
                                    self.eventAnalyzer.occurOnece(event)
                            else:
                                batTResTemp = sysDef.CloudBatteryTestResult.Failed
                                self.eventAnalyzer.occurOnece(self.EventID.ID_BATTERY_TEST_FAIL)

                        except Exception:
                            Logger.LogIns().logger.error(traceback.format_exc())
                    else:
                        config = Configuration()
                        config.selfTestResult = ispassed
                        batTDateTemp = self.device.dataSource.updateDeviceConfig(config)
                        self.batteryTesting = False

                        if ispassed:
                            batTResTemp = sysDef.CloudBatteryTestResult.Passed
                            self.eventAnalyzer.occurOnece(self.EventID.ID_BATTERY_TEST_PASS)

                        else:
                            batTResTemp = sysDef.CloudBatteryTestResult.Failed
                            self.eventAnalyzer.occurOnece(self.EventID.ID_BATTERY_TEST_FAIL)

                    continueFlag = True

            if continueFlag:  # 有BATTERY TEST結果
                Logger.LogIns().logger.info("decideSelfTest into #6")

                if self.device.cloudBtestFlag is True:
                    self.device.cloudBtestFlag = False # clear battery test flag
                else:  # 面板&軟體觸發Battery Test
                    self.device.cloudBtestResult = DevicePushMessageData.BatteryTestResult()
                    self.device.cloudBtestResult.BatTFrom = sysDef.CloudBatteryTestFrom.SW_PPP

                if batTResTemp is not None:
                    self.device.cloudBtestResult.BatTRes = batTResTemp

                if batTDateTemp is not None:
                    self.device.cloudBtestResult.BatTDate = int(time.mktime(batTDateTemp.timetuple()))  # datetime to UNIX time

        checkIsBatteryTesting = False
        if self.device.cloudBtestFlag is False:
            if not self.batteryTesting and deviceStatus.BatteryTesting is True:  # 面板&軟體觸發Battery Test
                checkIsBatteryTesting = True

            self.cloudBatteryTesting = False
        else:  # 雲端觸發Battery Test: cloudBtestFlag舉起代表已成功對UPS下BATTERY TEST指令
            if self.cloudBatteryTesting is False:
                checkIsBatteryTesting = True
                deviceStatus.BatteryTesting = True  # BATTERY TEST指令下成功overwrite deviceStatus, UI才會調整
                self.cloudBatteryTesting = True

        # check is battery testing
        if checkIsBatteryTesting is True:
            Logger.LogIns().logger.info("decideSelfTest into #7")
            self.batteryTesting = True
            self.eventAnalyzer.occurOnece(self.EventID.ID_BATTERY_TEST_START)  # 面板&軟體均由此觸發event

        return deviceStatus

    def decideTestEvent(self, testResult, resultType, testType):

        # Notice: Personal does not support battery calibration
        if testType == sysDef.TestType.TEST_TYPE_CALIBRATE:
            return None
        else:
            if resultType == sysDef.TestResultType.TEST_RESULT:

                if testResult == sysDef.TestResult.TEST_NOTHING:
                    return None
                if testResult == sysDef.TestResult.TEST_PASSED:
                    return self.EventID.ID_BATTERY_TEST_PASS
                if testResult == sysDef.TestResult.TEST_PROGRESSING:
                    return self.EventID.ID_BATTERY_TEST_START
                if testResult == sysDef.TestResult.TEST_WARNING:
                    return self.EventID.ID_BATTERY_TEST_INCOMPLETE
                if testResult == sysDef.TestResult.TEST_ERROR:
                    return None
                if testResult == sysDef.TestResult.TEST_ABORTED:
                    return self.EventID.ID_BATTERY_TEST_FAIL

            else:  # resultType == TestResultType.BATTERY_CALIBRATION_TEST_RESULT
                return None

    def getDeviceStatus(self, trx):
        deviceStatus = model_Json.DeviceStatusData.DeviceStatus()
        deviceStatus.deviceId = trx.deviceId

        if trx.deviceId is not -1:
            deviceStatus.InputStatus = self.decideInputStatus(trx)
            deviceStatus = self.decideBatteryStatus(trx, deviceStatus)
            deviceStatus = self.decideOutputStatus(trx, deviceStatus)
            deviceStatus = self.decideStatusProperty(trx, deviceStatus)

            # check is utility power falure
            if (((ValueId.ValueIdFinder().getValueId("STATUS_UTILITY_FAILURE") in trx.statementsDic)
                 and trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_UTILITY_FAILURE")].hasResults)):

                deviceStatus.UtilityPowerFailure = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_UTILITY_FAILURE")].results[0] == str(model_Json.DeviceStatusData.Utility.STATUS_POWER_FAILURE.value)


            if (((ValueId.ValueIdFinder().getValueId("STATUS_OUTPUT_OVERLOAD") in trx.statementsDic)
                 and trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_OUTPUT_OVERLOAD")].hasResults)):

                deviceStatus.OutputOverload = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_OUTPUT_OVERLOAD")].results[0] != str(0)

            if (((ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_CRITICAL") in trx.statementsDic)
                 and trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_CRITICAL")].hasResults)):

                deviceStatus.BatteryLow = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_CRITICAL")].results[0] != str(0)

            if (((ValueId.ValueIdFinder().getValueId("STATUS_RUNTIME_LOW") in trx.statementsDic)
                 and trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_RUNTIME_LOW")].hasResults)):

                deviceStatus.RuntimeLow = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_RUNTIME_LOW")].results[0] != str(0)

            # ************************UPS HARDWARE FAULT************************
            # hardwareFaultStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_HARDWARE_FAULT")]

            hardwareFaultStatement = None
            if ValueId.ValueIdFinder().getValueId("STATUS_HARDWARE_FAULT") in trx.statementsDic:
                hardwareFaultStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_HARDWARE_FAULT")]

            if hardwareFaultStatement is not None and hardwareFaultStatement.hasResults:
                b = hardwareFaultStatement.results[0] != str(0)
                # b = True # debug
                if b:
                    deviceStatus.UpsEventFlag = EventCodeLevelStatus.Fault.value

            if self.propertyFetcher.devicePropData.upsEventCode is not None and isinstance(self.propertyFetcher.devicePropData.upsEventCode.value, list) and len(self.propertyFetcher.devicePropData.upsEventCode.value) >0:
                if "C00.0" not in self.propertyFetcher.devicePropData.upsEventCode.value: # 若UPS無任何Event發生時，監控端仍詢問P66指令則UPS回應C00.0，代表UPS正常工作中

                    deviceStatus.UpsEventCode = self.propertyFetcher.devicePropData.upsEventCode.value  # type list, ex:['C51.1','C50.1']
                    lvList = []
                    maxLv = -1

                    for k, v in enumerate(deviceStatus.UpsEventCode):
                        if "." in v:
                            level_code = v.split(".")[1]  # ex: 0,1...
                            if len(level_code) > 0 and systemFunction.intTryParse(level_code):
                                lvList.append(int(level_code))

                    if len(lvList) > 0:
                        maxLv = max(lvList)

                    if maxLv <= 0:
                        deviceStatus.UpsEventFlag = EventCodeLevelStatus.Normal.value
                    elif 1 <= maxLv <= 3:
                        deviceStatus.UpsEventFlag = EventCodeLevelStatus.Waring.value
                    elif maxLv > 3:
                        deviceStatus.UpsEventFlag = EventCodeLevelStatus.Fault.value

                else:
                    deviceStatus.UpsEventCode = []
                    # deviceStatus.UpsEventCode = ['C51.1','C50.1'] # debug

        #有機會在底層斷線時，device id還沒被改為-1，所以多一個判斷若input volt, load watt, battery capacity都是空值，就回傳None讓上層認定未抓到Device
        if deviceStatus.deviceId != -1 and deviceStatus.InputVolt == None and deviceStatus.LoadWatt == None and deviceStatus.BatteryCapacity == None:
            Logger.LogIns().logger.info("lost but device id do not equals -1")
            deviceStatus.deviceId = -1
            return None
        return deviceStatus

    def decideInputStatus(self, trxData):
        try:
            valueIdFinder = ValueId.ValueIdFinder()  # ValueId Finder
            statementsDic = trxData.statementsDic  # 機器傳回資料
            inputStatus = None  # InputStatus Enum

            utilFail = False
            freqFail = False
            voltFail = False
            voltHighFail = False
            voltLowFail = False
            volt = None
            ratingVolt = None

            # utilFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")]
            # voltFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_VOLT_FAILURE")]
            # freqFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FREQ_FAILURE")]
            # voltStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_VOLT")]
            # avrStatement = statementsDic[valueIdFinder.getValueId("STATUS_AVR_LEVEL")]

            utilFailStatement = None
            voltFailStatement = None
            freqFailStatement = None
            voltStatement = None
            avrStatement = None

            if valueIdFinder.getValueId("STATUS_UTILITY_FAILURE") in statementsDic:
                utilFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")]

            if valueIdFinder.getValueId("STATUS_UTILITY_VOLT_FAILURE") in statementsDic:
                voltFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_VOLT_FAILURE")]

            if valueIdFinder.getValueId("STATUS_UTILITY_FREQ_FAILURE") in statementsDic:
                freqFailStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FREQ_FAILURE")]

            if valueIdFinder.getValueId("STATUS_UTILITY_VOLT") in statementsDic:
                voltStatement = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_VOLT")]

            if valueIdFinder.getValueId("STATUS_AVR_LEVEL") in statementsDic:
                avrStatement = statementsDic[valueIdFinder.getValueId("STATUS_AVR_LEVEL")]

            # Logger.LogIns().logger.info("[Monitor] UtilFailStatement: " + str(utilFailStatement))
            # Logger.LogIns().logger.info("[Monitor] voltFailStatement: " + str(voltFailStatement))
            # Logger.LogIns().logger.info("[Monitor] freqFailStatement: " + str(freqFailStatement))
            # Logger.LogIns().logger.info("[Monitor] voltStatement: " + str(voltStatement))
            # Logger.LogIns().logger.info("[Monitor] avrStatement: " + str(avrStatement))
            # self.printLog(utilFailStatement, "STATUS_UTILITY_FAILURE")
            # self.printLog(voltFailStatement, "STATUS_UTILITY_VOLT_FAILURE")
            # self.printLog(freqFailStatement, "STATUS_UTILITY_FREQ_FAILURE")
            # self.printLog(voltStatement, "STATUS_UTILITY_VOLT")
            # self.printLog(avrStatement, "STATUS_AVR_LEVEL")

            if utilFailStatement is not None and utilFailStatement.hasResults:
                utilFail = "1" in utilFailStatement.results[0]
                Logger.LogIns().logger.info("[Monitor] utilFailStatement.results[0]: " + str(utilFailStatement.results[0]))

            if freqFailStatement is not None and freqFailStatement.hasResults:
                freqFail = "1" in freqFailStatement.results[0]
                Logger.LogIns().logger.info("[Monitor] freqFailStatement.results[0]: " + str(freqFailStatement.results[0]))

            if voltFailStatement is not None and voltFailStatement.hasResults:
                voltFail = "1" in voltFailStatement.results[0]
                Logger.LogIns().logger.info("[Monitor] voltFailStatement.results[0]: " + str(voltFailStatement.results[0]))

            if voltStatement is not None and voltStatement.hasResults:
                volt = float(voltStatement.results[0]) / 1000
                Logger.LogIns().logger.info("[Monitor] voltStatement.results[0]: " + str(voltStatement.results[0]))

            if self.propertyFetcher.devicePropData.voltRating is not None:
                ratingVolt = int(self.propertyFetcher.devicePropData.voltRating.value)
                Logger.LogIns().logger.info("[Monitor] ratingVolt: " + str(int(self.propertyFetcher.devicePropData.voltRating.value)))

            if self.propertyFetcher.devicePropData.upperLimitProperty is not None:
                highTransfer = int(self.propertyFetcher.devicePropData.upperLimitProperty.value) * 0.98  # -2%誤差值
                Logger.LogIns().logger.info("[Monitor] highTransfer: " + str(int(self.propertyFetcher.devicePropData.upperLimitProperty.value)))

            if self.propertyFetcher.devicePropData.lowerLimitProperty is not None:
                lowTransfer = int(self.propertyFetcher.devicePropData.lowerLimitProperty.value) * 1.02  # +2%誤差值
                Logger.LogIns().logger.info("[Monitor] lowTransfer: " + str(int(self.propertyFetcher.devicePropData.lowerLimitProperty.value)))

            Logger.LogIns().logger.info("[Monitor] *utilFail: " + str(utilFail))
            Logger.LogIns().logger.info("[Monitor] *voltFail: " + str(voltFail))
            Logger.LogIns().logger.info("[Monitor] *freqFail: " + str(freqFail))
            Logger.LogIns().logger.info("[Monitor] *volt: " + str(volt))
            Logger.LogIns().logger.info("[Monitor] *ratingVolt: " + str(ratingVolt))
            Logger.LogIns().logger.info("[Monitor] *lowTransfer: " + str(lowTransfer))
            Logger.LogIns().logger.info("[Monitor] *highTransfer: " + str(highTransfer))

            # prepare condition reference PPBE DeviceStatus.java line 2689
            if utilFail and not voltFail and not freqFail:
                voltFail = True
            if utilFail:
                if voltFail:
                    if freqFail or volt < 60:
                        inputStatus = DeviceStatusData.InputStatus.UtilityFailure.value
                    # elif volt < ratingVolt:
                    elif volt <= lowTransfer:
                        inputStatus = DeviceStatusData.InputStatus.UtilityLow.value
                    # elif volt > ratingVolt:
                    elif volt >= highTransfer:
                        inputStatus = DeviceStatusData.InputStatus.UtilityHigh.value
                    else:
                        inputStatus = DeviceStatusData.InputStatus.UtilityFailure.value
                else:
                    inputStatus = DeviceStatusData.InputStatus.FreqFailure.value

            if inputStatus is None:
                inputStatus = DeviceStatusData.InputStatus.Normal.value

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

        Logger.LogIns().logger.info("[Monitor] *inputStatus: " + str(inputStatus))
        return inputStatus

    def decideBatteryStatus(self, trxData, deviceStatus):
        try:
            valueIdFinder = ValueId.ValueIdFinder()  # ValueId Finder
            statementsDic = trxData.statementsDic  # 機器傳回資料
            batteryStatus = model_Json.DeviceStatusData.BatteryStatus  # BatteryStatus Enum

            disChargFlag_Pre = ((valueIdFinder.getValueId("STATUS_DISCHARGING") in statementsDic) and statementsDic[
                valueIdFinder.getValueId("STATUS_DISCHARGING")].hasResults)

            chargFlag_Pre = ((valueIdFinder.getValueId("STATUS_CHARGING") in statementsDic) and statementsDic[
                valueIdFinder.getValueId("STATUS_CHARGING")].hasResults)

            fulChargFlag_Pre = ((valueIdFinder.getValueId("STATUS_FULL_CHARGED") in statementsDic) and statementsDic[
                valueIdFinder.getValueId("STATUS_FULL_CHARGED")].hasResults)

            # batteryTestingStatement = statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_TESTING")]

            batteryTestingStatement = None
            if valueIdFinder.getValueId("STATUS_BATTERY_TESTING") in statementsDic:
                batteryTestingStatement = statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_TESTING")]

            batteryTesting_Pre = batteryTestingStatement is not None and batteryTestingStatement.hasResults

            if batteryTestingStatement is not None and (batteryTestingStatement.errCode != model_Json.DeviceStatusData.ErrorCode.DRVERR_SUCCESS.value):
                self.isSelfTestFailFlag = True

            hardwareFault_Pre = ((valueIdFinder.getValueId("STATUS_HARDWARE_FAULT") in statementsDic) and statementsDic[
                valueIdFinder.getValueId("STATUS_HARDWARE_FAULT")].hasResults)

            if disChargFlag_Pre:
                id27 = statementsDic[valueIdFinder.getValueId("STATUS_DISCHARGING")].results[0]

                if (id27 == str(1)):
                    deviceStatus.BatteryStatus = batteryStatus.Discharging.value

            if chargFlag_Pre:
                id26 = statementsDic[valueIdFinder.getValueId("STATUS_CHARGING")].results[0]

                if (id26 == str(1)):
                    deviceStatus.BatteryStatus = batteryStatus.Charging.value

            if fulChargFlag_Pre:
                id173 = statementsDic[valueIdFinder.getValueId("STATUS_FULL_CHARGED")].results[0]

                if (id173 == str(1)):
                    deviceStatus.BatteryStatus = batteryStatus.FullCharge.value

            if batteryTesting_Pre:
                deviceStatus.BatteryTesting = int(statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_TESTING")].results[0]) == 1 # BatteryTesting為True表示self-test進行中

            if hardwareFault_Pre:
                deviceStatus.HardwareFault = int(statementsDic[valueIdFinder.getValueId("STATUS_HARDWARE_FAULT")].results[0]) == 1 # HardwareFault為True表示Hardware has fault

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

        return deviceStatus

    def decideOutputStatus(self, trxData, deviceStatus):
        valueIdFinder = ValueId.ValueIdFinder()  # ValueId Finder
        statementsDic = trxData.statementsDic  # 機器傳回資料
        outputStatus = model_Json.DeviceStatusData.OutputStatus  # OutputStatus Enum

        utilPowFlag_Pre = ((valueIdFinder.getValueId("STATUS_UTILITY_FAILURE") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")].hasResults)

        batteryPowFlag_Pre = ((valueIdFinder.getValueId("STATUS_UTILITY_FAILURE") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")].hasResults)

        noOutputFlag_Pre = ((valueIdFinder.getValueId("STATUS_OUTPUT_OFF") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_OFF")].hasResults)

        disChargFlag_Pre = ((valueIdFinder.getValueId("STATUS_DISCHARGING") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_DISCHARGING")].hasResults)

        overload_flag_pre = ((valueIdFinder.getValueId("STATUS_OUTPUT_OVERLOAD") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_OVERLOAD")].hasResults)

        avr_level_flag_pre = ((valueIdFinder.getValueId("STATUS_AVR_LEVEL") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_AVR_LEVEL")].hasResults)

        bypass_flag_pre = ((valueIdFinder.getValueId("STATUS_BYPASS_ACTIVE") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_BYPASS_ACTIVE")].hasResults)

        manual_bypass_flag_pre = ((valueIdFinder.getValueId("STATUS_MANUAL_BYPASS") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_MANUAL_BYPASS")].hasResults)

        bypass_overload_flag_pre = ((valueIdFinder.getValueId("STATUS_BYPASS_OVERLOAD") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_BYPASS_OVERLOAD")].hasResults)

        status_eco_flag_pre = ((valueIdFinder.getValueId("OUTPUT_STATUS_ECO") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("OUTPUT_STATUS_ECO")].hasResults)


        Logger.LogIns().logger.info("[Monitor] utilPowFlag_Pre: " + str(utilPowFlag_Pre))
        Logger.LogIns().logger.info("[Monitor] batteryPowFlag_Pre: " + str(batteryPowFlag_Pre))
        Logger.LogIns().logger.info("[Monitor] noOutputFlag_Pre: " + str(noOutputFlag_Pre))
        Logger.LogIns().logger.info("[Monitor] disChargFlag_Pre: " + str(disChargFlag_Pre))

        # 紀錄一下，Output Status的狀態應該要能並存，這次把Output Status狀態缺的補齊但還沒改並存
        if utilPowFlag_Pre:
            id11 = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")].results[0]

            if id11 == str(0):

                Logger.LogIns().logger.info("[Monitor] id11: " + str(id11))

                # Frequency Failure需顯示battery mode
                # frequency fail不會舉起utility fail, 用discharging判斷
                if disChargFlag_Pre:
                    id27 = statementsDic[valueIdFinder.getValueId("STATUS_DISCHARGING")].results[0]

                    if id27 == str(1):

                        Logger.LogIns().logger.info("[Monitor] id27: " + str(id27))

                        deviceStatus.OutputStatus = outputStatus.BatteryPower.value
                        deviceStatus.PowerSourceStatus = outputStatus.BatteryPower.value
                    else:
                        deviceStatus.OutputStatus = outputStatus.UtilityPower.value
                        deviceStatus.PowerSourceStatus = outputStatus.UtilityPower.value
                else:
                    deviceStatus.OutputStatus = outputStatus.UtilityPower.value
                    deviceStatus.PowerSourceStatus = outputStatus.UtilityPower.value

        if batteryPowFlag_Pre:
            id11 = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FAILURE")].results[0]

            if id11 == str(1):
                deviceStatus.OutputStatus = outputStatus.BatteryPower.value
                deviceStatus.PowerSourceStatus = outputStatus.BatteryPower.value

        if noOutputFlag_Pre:
            id158 = statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_OFF")].results[0]

            if id158 == str(1):
                Logger.LogIns().logger.info("[Monitor] id158: " + str(id158))

                deviceStatus.OutputStatus = outputStatus.NoOutput.value
                deviceStatus.PowerSourceStatus = outputStatus.NoOutput.value
        if overload_flag_pre:
            overload = statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_OVERLOAD")].results[0]

            if overload == str(1):
                deviceStatus.OutputStatus = outputStatus.Overload.value
        if bypass_flag_pre:
            if manual_bypass_flag_pre:
                manual_bypass = statementsDic[valueIdFinder.getValueId("STATUS_MANUAL_BYPASS")].results[0]

                if manual_bypass == str(1):
                    deviceStatus.OutputStatus = outputStatus.ManualBypass.value
            elif status_eco_flag_pre:
                eco_mode = statementsDic[valueIdFinder.getValueId("OUTPUT_STATUS_ECO")].results[0]

                if eco_mode == str(1):
                    deviceStatus.OutputStatus = outputStatus.EcoMode.value
            else:
                bypass = statementsDic[valueIdFinder.getValueId("STATUS_BYPASS_ACTIVE")].results[0]

                if bypass == str(1):
                    deviceStatus.OutputStatus = outputStatus.Bypass.value


        if avr_level_flag_pre:
            avr_level = statementsDic[valueIdFinder.getValueId("STATUS_AVR_LEVEL")].results[0]

            if avr_level == str(1) or avr_level == str(2):
                deviceStatus.OutputStatus = outputStatus.Boost.value
            elif avr_level == str(3):
                deviceStatus.OutputStatus = outputStatus.Buck.value



        if bypass_overload_flag_pre:
            bypass_overload = statementsDic[valueIdFinder.getValueId("STATUS_BYPASS_OVERLOAD")].results[0]

            if bypass_overload == str(1):
                deviceStatus.OutputStatus = outputStatus.BypassOverload.value

        return deviceStatus

    def decideStatusProperty(self, trxData, deviceStatus):
        valueIdFinder = ValueId.ValueIdFinder()  # ValueId Finder
        statementsDic = trxData.statementsDic  # 機器傳回資料

        # 從底層拿新的欄位，因舊的邏輯寫法會取得flag_pre再做判斷，這次沒有去理解這個做法的用意，但因為新拿的資料不需要做這樣的判斷
        # 所以我直接判斷有沒有值直接assign
        if ((valueIdFinder.getValueId("STATUS_UTILITY_VOLT") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_UTILITY_VOLT")].hasResults):
            deviceStatus.InputVolt = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_VOLT")].results[0]

        if ((valueIdFinder.getValueId("STATUS_UTILITY_FREQ") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_UTILITY_FREQ")].hasResults):
            deviceStatus.InputFreq = statementsDic[valueIdFinder.getValueId("STATUS_UTILITY_FREQ")].results[0]

        if ((valueIdFinder.getValueId("STATUS_OUTPUT_FREQ") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_FREQ")].hasResults):
            deviceStatus.OutputFreq = statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_FREQ")].results[0]

        if ((valueIdFinder.getValueId("STATUS_OUTPUT_CURRENT") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_CURRENT")].hasResults):
            deviceStatus.OutputCurrent = statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_CURRENT")].results[0]

        if ((valueIdFinder.getValueId("STATUS_BATTERY_VOLT") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_BATTERY_VOLT")].hasResults):
            deviceStatus.BatteryVolt = statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_VOLT")].results[0]

        if ((valueIdFinder.getValueId("STATUS_TEMPERATURE") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_TEMPERATURE")].hasResults):
            deviceStatus.UpsTemperature = statementsDic[valueIdFinder.getValueId("STATUS_TEMPERATURE")].results[0]

        # ---end

        voltFlag_Pre = ((valueIdFinder.getValueId("STATUS_OUTPUT_VOLT") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_VOLT")].hasResults)

        batteryCapFlag_Pre = ((valueIdFinder.getValueId("STATUS_BATTERY_CAPACITY") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_BATTERY_CAPACITY")].hasResults)

        remainRuntimeFlag_Pre = ((valueIdFinder.getValueId("STATUS_REMAIN_RUNTIME") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_REMAIN_RUNTIME")].hasResults)

        # loadWattFlag_Pre是判斷是否有取到UPS Load Percentage的旗標
        loadWattFlag_Pre = ((valueIdFinder.getValueId("STATUS_PERCENT_LOAD") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_PERCENT_LOAD")].hasResults)

        # outputLoadWattFlag_Pre是判斷是否有取到UPS Load Watt的旗標
        outputLoadWattFlag_Pre = ((valueIdFinder.getValueId("STATUS_OUTPUT_WATT") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("STATUS_OUTPUT_WATT")].hasResults)

        activePowerFlag_Pre = ((valueIdFinder.getValueId("PROP_ACTIVE_POWER") in statementsDic) and statementsDic[
            valueIdFinder.getValueId("PROP_ACTIVE_POWER")].hasResults)

        if voltFlag_Pre:
            deviceStatus.OutputVolt = statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_VOLT")].results[0]

        if batteryCapFlag_Pre:
            deviceStatus.BatteryCapacity = statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_CAPACITY")].results[0]

            cap_f = systemFunction.stringParse2Float(deviceStatus.BatteryCapacity)
            if cap_f > float(100.0):
                deviceStatus.BatteryCapacity = str(100 * 1000)

        if remainRuntimeFlag_Pre:
            deviceStatus.RemainingRuntime = statementsDic[valueIdFinder.getValueId("STATUS_REMAIN_RUNTIME")].results[0]

        if outputLoadWattFlag_Pre:
            try:
                deviceStatus.LoadWatt = float(0)
                if systemFunction.intTryParse(statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_WATT")].results[0]):
                    deviceStatus.LoadWatt = int(statementsDic[valueIdFinder.getValueId("STATUS_OUTPUT_WATT")].results[0]) / 1000
            except Exception:
                Logger.LogIns().logger.error(traceback.format_exc())
        elif loadWattFlag_Pre and self.propertyFetcher.devicePropData.activePower is not None:
            activePower = None
            try:
                deviceStatus.LoadWatt = float(0)
                if systemFunction.floatTryParse(statementsDic[valueIdFinder.getValueId("STATUS_PERCENT_LOAD")].results[0]):
                    percentLoad = float(statementsDic[valueIdFinder.getValueId("STATUS_PERCENT_LOAD")].results[0]) / 1000 / 100  # 轉%
                    deviceStatus.PercentLoad = percentLoad

                if self.propertyFetcher.devicePropData.activePower is not None and self.propertyFetcher.devicePropData.activePower.value != sysDef.unknownStr:
                    activePower = float(self.propertyFetcher.devicePropData.activePower.value)

                if percentLoad is not None and activePower is not None:
                    deviceStatus.LoadWatt = round(percentLoad * activePower, 0)  # 取整數四捨五入
            except Exception:
                Logger.LogIns().logger.error(traceback.format_exc())

        return deviceStatus

    """取得Device狀態"""

    def fetchDeviceStatus(self, helper, deviceId):

        valueIdFinder = ValueId.ValueIdFinder()  # ValueId Finder
        trx = Transaction.Transaction()
        trx.setDeviceId(deviceId)

        utilityVoltStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_VOLT"))
        utilityFreqStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_FREQ"))
        utilityAmpStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_CURRENT"))
        utilityPowerFactorStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_POWER_FACTOR"))
        utilityFailureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_FAILURE"))
        utilityVoltFailureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_VOLT_FAILURE"))
        utilityFreqFailureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_FREQ_FAILURE"))
        utilityWiringFaultStat = Statement.Statement(valueIdFinder.getValueId("STATUS_WIRING_FAULT"))
        utilityNoNeutralStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_NO_NEUTRAL"))
        utilityGeneratorDetectedStat = Statement.Statement(valueIdFinder.getValueId("STATUS_UTILITY_GENERATOR_DETECTED"))

        # Output
        outputVoltStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_VOLT"))
        outputLoadStat = Statement.Statement(valueIdFinder.getValueId("STATUS_PERCENT_LOAD"))
        outputLoadWattStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_WATT"))
        outputFreqStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_FREQ"))
        outputCurrentStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_CURRENT"))
        outputPowerFactorStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_POWER_FACTOR"))
        outputActivePowerStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_ACTIVE_POWER"))
        outputApparentPowerStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_APPARENT_POWER"))
        outputReactivePowerStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_REACTIVE_POWER"))
        outputFreqFailureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_FREQ_FAILURE"))
        outputVoltFailureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_VOLT_FAILURE"))
        outputOverloadStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_OVERLOAD"))
        avrLevelStat = Statement.Statement(valueIdFinder.getValueId("STATUS_AVR_LEVEL"))
        outputNoOutputStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_OFF"))

        outputEmergencyPowerOffStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_EMERGENCY_POWER_OFF"))
        bypassActiveStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BYPASS_ACTIVE"))
        bypassOverloadStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BYPASS_OVERLOAD"))
        batteryVoltStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_VOLT"))
        batteryCurrentStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_CURRENT"))
        batteryCapacityStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_CAPACITY"))
        remainingRuntimeStat = Statement.Statement(valueIdFinder.getValueId("STATUS_REMAIN_RUNTIME"))
        remainingChargeTimeStat = Statement.Statement(valueIdFinder.getValueId("STATUS_REMAIN_CHARGETIME"))
        batteryTemperatureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_TEMPERATURE"))
        batteryCapacityLowStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_CRITICAL"))
        batteryChargingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_CHARGING"))
        batteryDischargingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_DISCHARGING"))
        batteryNotPresentStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_NOT_PRESENT"))
        batteryTestingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_TESTING"))
        batteryFullChargedStat = Statement.Statement(valueIdFinder.getValueId("STATUS_FULL_CHARGED"))
        batteryExhaustedStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_EXHAUSTED"))
        batteryConnectionReversedStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_CONNECTION_REVERSED"))
        batteryFloatChargingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_FLOAT_CHARGING"))
        batteryBoostChargingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_BOOST_CHARGING"))
        temperatureStat = Statement.Statement(valueIdFinder.getValueId("STATUS_TEMPERATURE"))
        overheatStat = Statement.Statement(valueIdFinder.getValueId("STATUS_INV_OVERHEAT"))
        inverterOffStat = Statement.Statement(valueIdFinder.getValueId("STATUS_INV_OFF"))
        hardwareFaultStat = Statement.Statement(valueIdFinder.getValueId("STATUS_HARDWARE_FAULT"))
        hardwareFaultCodeStat = Statement.Statement(valueIdFinder.getValueId("STATUS_FAULT_CODE"))
        originalHardwareFaultCodeStat = Statement.Statement(valueIdFinder.getValueId("STATUS_HARDWARE_FAULT_CODE"))
        systemMaintenanceBreakStat = Statement.Statement(valueIdFinder.getValueId("STATUS_SYSTEM_MAINTENANCE_BREAK"))
        outletStateStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTLET_STATE"))
        outletAutoOffPendingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTLET_SHUTDOWN_DELAY_PENDING"))
        outletAutoOnPendingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTLET_RESTORE_DELAY_PENDING"))
        outletManualOffPendingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTLET_SHUTDOWN_SCHEDULE_PENDING"))
        outletManualOnPendingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTLET_RESTORE_SCHEDULE_PENDING"))
        configChangIdeStat = Statement.Statement(valueIdFinder.getValueId("STATUS_CONFIG_CHANGE_ID"))
        testResultStat = Statement.Statement(valueIdFinder.getValueId("STATUS_TEST_RESULT"))
        batteryTestResultStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_TEST_RESULT"))
        calibrationTestResultStat = Statement.Statement(valueIdFinder.getValueId("STATUS_CALIBRATION_TEST_RESULT"))
        buzzerBeepingStat = Statement.Statement(valueIdFinder.getValueId("STATUS_BUZZER_BEEPING"))
        runtimeLowStat = Statement.Statement(valueIdFinder.getValueId("STATUS_RUNTIME_LOW"))

        outputShortedStat = Statement.Statement(valueIdFinder.getValueId("STATUS_OUTPUT_SHORTED"))
        outputECOModeStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_ECO_MODE"))
        bypassOverloadStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_BYPASS_OVERLOAD"))
        hardwareFaultStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_HARDWARE_FAULT"))
        utilityWiringFaultStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_WIRING_FAULT"))
        batteryNeedReplaceStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_REPLACE"))

        # upsEventStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_UPS_EVENT"))
        # upsEventCodeStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_UPS_EVENT_CODE"))

        trx.add(utilityVoltStat)
        trx.add(utilityFreqStat)
        trx.add(utilityAmpStat)
        trx.add(utilityPowerFactorStat)
        trx.add(utilityFailureStat)
        trx.add(utilityVoltFailureStat)
        trx.add(utilityFreqFailureStat)
        trx.add(utilityWiringFaultStat)
        trx.add(utilityNoNeutralStat)
        trx.add(utilityGeneratorDetectedStat)
        trx.add(outputVoltStat)
        trx.add(outputLoadStat)
        trx.add(outputLoadWattStat)
        trx.add(outputFreqStat)
        trx.add(outputCurrentStat)
        trx.add(outputPowerFactorStat)
        trx.add(outputActivePowerStat)
        trx.add(outputApparentPowerStat)
        trx.add(outputReactivePowerStat)
        trx.add(outputFreqFailureStat)
        trx.add(outputVoltFailureStat)
        trx.add(outputOverloadStat)
        trx.add(avrLevelStat)
        trx.add(outputNoOutputStat)
        trx.add(outputEmergencyPowerOffStat)
        trx.add(bypassActiveStat)
        trx.add(bypassOverloadStat)
        trx.add(batteryVoltStat)
        trx.add(batteryCurrentStat)
        trx.add(batteryCapacityStat)
        trx.add(remainingRuntimeStat)
        trx.add(remainingChargeTimeStat)
        trx.add(batteryTemperatureStat)
        trx.add(batteryCapacityLowStat)
        trx.add(batteryChargingStat)
        trx.add(batteryDischargingStat)
        trx.add(batteryNotPresentStat)
        trx.add(batteryTestingStat)
        trx.add(batteryFullChargedStat)
        trx.add(batteryExhaustedStat)
        trx.add(batteryConnectionReversedStat)
        trx.add(batteryFloatChargingStat)
        trx.add(batteryBoostChargingStat)
        trx.add(temperatureStat)
        trx.add(overheatStat)
        trx.add(inverterOffStat)
        trx.add(hardwareFaultStat)
        trx.add(hardwareFaultCodeStat)
        trx.add(originalHardwareFaultCodeStat)
        trx.add(systemMaintenanceBreakStat)
        trx.add(outletStateStat)
        trx.add(outletAutoOffPendingStat)
        trx.add(outletAutoOnPendingStat)
        trx.add(outletManualOffPendingStat)
        trx.add(outletManualOnPendingStat)
        trx.add(configChangIdeStat)
        trx.add(testResultStat)
        trx.add(batteryTestResultStat)
        trx.add(calibrationTestResultStat)
        trx.add(buzzerBeepingStat)
        trx.add(runtimeLowStat)

        trx.add(outputShortedStat)
        trx.add(outputECOModeStatement)
        trx.add(bypassOverloadStatement)
        trx.add(hardwareFaultStatement)
        trx.add(utilityWiringFaultStatement)
        trx.add(batteryNeedReplaceStatement)

        # trx.add(upsEventStatement)
        # trx.add(upsEventCodeStatement)

        flag = helper.submit(trx)  # Get transaction from device

        if (not flag) or (trx.state != model_Json.DeviceStatusData.DeviceState.PROXY_STATE_NORMAL.value):
            Logger.LogIns().logger.info("flag: " + str(flag))
            Logger.LogIns().logger.info("trx.statetrx.state: " + str(trx.state))
            return False

        self.transactionData = trx

        if configChangIdeStat.errCode == 0 and configChangIdeStat.hasResults:
            if systemFunction.intTryParse(configChangIdeStat.results[0]):
                self.configChangeId = int(configChangIdeStat.results[0])

        self.deviceId = trx.deviceId  # 更新deviceId

        return True

    def setDeviceStatusToSilenceMsg(self, deviceStatus):

        if deviceStatus is not None:
            # "PowSour": 0, <- Power Source, 值域:0/1, (Utility/Battery)
            self.device.devicePushSilenceMsg.PowSour = 0 if deviceStatus.InputStatus == DeviceStatusData.InputStatus.Normal.value else 1

            if deviceStatus.deviceId == -1:
                self.device.devicePushSilenceMsg.upsState = sysDef.UPS_StateMobile.Unable_to_establish_communication_with_UPS.value
            else:
                self.device.devicePushSilenceMsg.upsState = sysDef.UPS_StateMobile.The_UPS_is_working_normally.value

            if not systemFunction.stringIsNullorEmpty(deviceStatus.OutputVolt):
                self.device.devicePushSilenceMsg.OutVolt = round(systemFunction.stringParse2Float(deviceStatus.OutputVolt))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.OutputFreq):
                self.device.devicePushSilenceMsg.OutFreq = round(systemFunction.stringParse2Float(deviceStatus.OutputFreq))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.OutputCurrent):
                self.device.devicePushSilenceMsg.OutCur = round(systemFunction.stringParse2Float(deviceStatus.OutputCurrent))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.InputFreq):
                self.device.devicePushSilenceMsg.InFreq = round(systemFunction.stringParse2Float(deviceStatus.InputFreq))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.InputVolt):
                self.device.devicePushSilenceMsg.InVolt = round(systemFunction.stringParse2Float(deviceStatus.InputVolt))

            # self.device.devicePushSilenceMsg.InSta = deviceStatus.InputStatus
            # self.device.devicePushSilenceMsg.OutSta = deviceStatus.OutputStatus
            self.device.devicePushSilenceMsg.OutSta = DeviceStatusData.OutputStatus(deviceStatus.OutputStatus).get_publish_output_status()
            self.device.devicePushSilenceMsg.InSta = DeviceStatusData.InputStatus(deviceStatus.InputStatus).get_publish_input_status()

            if not systemFunction.stringIsNullorEmpty(deviceStatus.BatteryCapacity):
                # self.device.devicePushSilenceMsg.capacity = "{0:.0f} %".format(systemFunction.stringParse2Float(deviceStatus.BatteryCapacity))
                self.device.devicePushSilenceMsg.BatCap = systemFunction.stringParse2Float(deviceStatus.BatteryCapacity)

            self.device.devicePushSilenceMsg.BatSta = deviceStatus.BatteryStatus

            if not systemFunction.stringIsNullorEmpty(deviceStatus.RemainingRuntime):
                self.device.devicePushSilenceMsg.BatRun = round(systemFunction.stringParse2Min(deviceStatus.RemainingRuntime))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.BatteryVolt):
                self.device.devicePushSilenceMsg.BatVolt = systemFunction.stringParse2Float(deviceStatus.BatteryVolt)

            self.device.devicePushSilenceMsg.Load = deviceStatus.LoadWatt

            if not systemFunction.stringIsNullorEmpty(deviceStatus.UpsTemperature):
                self.device.devicePushSilenceMsg.SysTemp = systemFunction.stringParse2Float(deviceStatus.UpsTemperature)

        if self.device.cloudBtestResult is not None and self.device.cloudBtestResult.BatTRes is not None:
            self.device.devicePushSilenceMsg.BatTRes = self.device.cloudBtestResult.BatTRes
            self.device.devicePushSilenceMsg.BatTDate = self.device.cloudBtestResult.BatTDate
            self.device.devicePushSilenceMsg.BatTFrom = self.device.cloudBtestResult.BatTFrom
            self.device.cloudBtestResult = None # clear

    def eventDictInit(self):
        data = self.device.eventEnum
        if len(data) > 0:
            for item in data:
                self.event_number_dict[item.reasoning] = item.number

    def printLog(self, stat, ValueId):
        try:
            f1 = True
            if stat is None:
                Logger.LogIns().logger.info("***[Monitor] stat: {0} is None ***".format(ValueId))
                f1 = False

            f2 = True
            if not stat.hasResults:
                Logger.LogIns().logger.info("***[Monitor] stat: {0} not hasResults ***".format(ValueId))
                f2 = False

            if f1 and f2:
                Logger.LogIns().logger.info("***[Monitor] stat: {0} value = {1} ***".format(ValueId, str(stat.results)))
        except Exception:
            traceback.print_exc(file=sys.stdout)

