import sys, time, traceback, platform
from Events import EventsMobile
from System import systemFunction, settings, ValueId
from Utility import Scheduler, Logger, OSOperator
from controllers import MobileDataProvider, WebAppController
from controllers.DeviceConfigure import DeviceConfigure
from model_Json import DataSource2, DevicePushMessageData
from model_Json.DeviceStatusData import *
from views.Custom import ViewData
from model_Json.tables.Configuration import Configuration
from Utility import Logger, ShutdownUtil


class EventAnalyzer(object):
    def __init__(self, server ,device):
        self.EventID = device.cloudEventId
        self.eventOccuredRecord = []
        self.isUtilityFailure = False
        self.deviceConfigure = DeviceConfigure()
        self.device = device
        self.server = server
        self.dataSource = device.dataSource
        # self.schedulerManager = Scheduler.SchedulerManager(self.device.desktopInteractiveServer)
        self.schedulerManager = self.device.schedulerManager
        self.dataSource.runtimeChangeConfigSignal.connect(self.restartShutdownAction)
        self.isReConfig = False
        self.WebAppController = WebAppController.WebAppController(device)

        # PPP mobile solution"
        self.fcmProvider = MobileDataProvider.FcmMsgProvider(device)
        self.EventMoble = EventsMobile.EventCloud(device)

        # cloud events
        self.batteryCharging = -1  # 0:false, 1:true, -1:unavailable
        self.batteryDischarging = -1  # 0:false, 1:true, -1:unavailable
        self.batteryNotPresent = -1  # 0:false, 1:true, -1:unavailable
        self.outputShorted = -1  # 0:false, 1:true, -1:unavailable
        self.outputOverload = -1  # 0:false, 1:true, -1:unavailable
        self.overheat = -1  # 0:false, 1:true, -1:unavailable
        self.batteryExhausted = -1  # 0:false, 1:true, -1:unavailable
        self.batteryCritical = -1  # 0:false, 1:true, -1:unavailable
        self.hardwareFault = -1  # 0:false, 1:true, -1:unavailable
        self.batteryTesting = -1  # 0:false, 1:true, -1:unavailable
        self.lastTrxData = None
        self.batteryFullyCharged = -1  # -1: init, 0: false, 1: true
        self.batteryNeedReplaceAlert = False
        self.outputStopSoon = 0  # 0:false, 1:true, -1:unavailable

        # UPS event code
        self.lastUpsEventCode = []
        self.eventCodeRestore = []
        self.eventCodeNew = []

        self.server.eventOccurSignal.connect(self.occurOnece)
        self.server.shutdownAlertSignal.connect(self.occur)

    def checkDeviceStatus(self):
        print(self.device.deviceStatus.InputVolt)

    def analyze(self, deviceStatus, transactionData):
        try:
            self.isShutdown = False
            self.printFlag(True)
            Logger.LogIns().logger.info("***[EventAnalyzer] analyze InputStatus: {0} ***".format(str(deviceStatus.InputStatus)))
            Logger.LogIns().logger.info("***[EventAnalyzer] analyze SelfTestFWErrFlag: {0} ***".format(str(deviceStatus.SelfTestFWErrFlag)))

            # Utility High
            if deviceStatus.InputStatus == InputStatus.UtilityHigh.value and not self.isUtilityFailure:
                if deviceStatus.SelfTestFWErrFlag:
                    self.occur(self.EventID.ID_UTILITY_TRANSFER_HIGH)
                    self.isUtilityFailure = True

            # Utility Low
            if deviceStatus.InputStatus == InputStatus.UtilityLow.value and not self.isUtilityFailure:
                if deviceStatus.SelfTestFWErrFlag:
                    self.occur(self.EventID.ID_UTILITY_TRANSFER_LOW)
                    self.isUtilityFailure = True

            # Power Outage this occur need after high and low
            if deviceStatus.UtilityPowerFailure and not self.isUtilityFailure:
                if deviceStatus.SelfTestFWErrFlag:
                    self.occur(self.EventID.ID_UTILITY_FAILURE)
                    self.isUtilityFailure = True
                    print("failure")

            if deviceStatus.OutputStatus == OutputStatus.Boost.value:
                self.occur(self.EventID.ID_AVR_BOOST_ACTIVE)
                print("avr boost")

            if deviceStatus.OutputStatus == OutputStatus.Buck.value:
                self.occur(self.EventID.ID_AVR_BUCK_ACTIVE)
                print("avr bucket")

            # restore check
            if not deviceStatus.UtilityPowerFailure and self.isUtilityFailure:
                self.restoreOccur(self.EventID.ID_UTILITY_FAILURE_RESTORE)
                self.restoreOccur(self.EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE)
                self.restoreOccur(self.EventID.ID_UTILITY_TRANSFER_LOW_RESTORE)
                self.isUtilityFailure = False
                print("not failure")

            if deviceStatus.OutputStatus == OutputStatus.UtilityPower.value:
                self.restoreOccur(self.EventID.ID_AVR_BOOST_RESTORE)
                self.restoreOccur(self.EventID.ID_AVR_BUCK_RESTORE)
                print("STATUS Normal")

            trx = transactionData

            batteryTestingStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_TESTING")]
            self.printLog(batteryTestingStatement, "STATUS_BATTERY_TESTING")
            if batteryTestingStatement is not None and batteryTestingStatement.hasResults:
                b = batteryTestingStatement.results[0] != str(0)

                if b and self.batteryTesting == 0:  # initiate
                    # self.occurOnece(self.EventID.ID_BATTERY_TEST_START)
                    pass

                if b:
                    self.batteryTesting = 1
                else:
                    self.batteryTesting = 0

            batteryChargingStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_CHARGING")]
            self.printLog(batteryChargingStatement, "STATUS_CHARGING")
            if batteryChargingStatement is not None and batteryChargingStatement.hasResults:
                b = batteryChargingStatement.results[0] != str(0)

                if b and self.batteryCharging != 1:
                    self.occurOnece(self.EventID.ID_BATTERY_CHARGING_START)

                elif not b and self.batteryCharging == 1:
                    self.occurOnece(self.EventID.ID_BATTERY_CHARGING_STOP)

                if b:
                    self.batteryCharging = 1
                else:
                    self.batteryCharging = 0

            batteryDischargingStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_DISCHARGING")]
            self.printLog(batteryDischargingStatement, "STATUS_DISCHARGING")
            if batteryDischargingStatement is not None and batteryDischargingStatement.hasResults:
                b = batteryDischargingStatement.results[0] != str(0)

                if b and self.batteryDischarging != 1:
                    self.occurOnece(self.EventID.ID_BATTERY_DISCHARGING_START)

                elif not b and self.batteryDischarging == 1:
                    self.occurOnece(self.EventID.ID_BATTERY_DISCHARGING_STOP)

                if b:
                    self.batteryDischarging = 1
                else:
                    self.batteryDischarging = 0

            batteryNotPresentStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_NOT_PRESENT")]
            self.printLog(batteryNotPresentStatement, "STATUS_BATTERY_NOT_PRESENT")
            if batteryNotPresentStatement is not None and batteryNotPresentStatement.hasResults:
                b = batteryNotPresentStatement.results[0] != str(0)

                if b and self.batteryNotPresent != 1:
                    self.occurOnece(self.EventID.ID_BATTERY_NOT_PRESENT)

                elif not b and self.batteryNotPresent == 1:
                    self.occurOnece(self.EventID.ID_BATTERY_NOT_PRESENT_RESTORE)

                if b:
                    self.batteryNotPresent = 1
                else:
                    self.batteryNotPresent = 0

            outputShortedStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_OUTPUT_SHORTED")]
            self.printLog(outputShortedStatement, "STATUS_OUTPUT_SHORTED")
            if outputShortedStatement is not None and outputShortedStatement.hasResults:
                b = outputShortedStatement.results[0] != str(0)

                if b and self.outputShorted != 1:
                    self.occurOnece(self.EventID.ID_OUTPUT_CIRCUIT_SHORT)

                elif not b and self.outputShorted == 1:
                    self.occurOnece(self.EventID.ID_OUTPUT_IS_NO_LONGER_CIRCUIT_SHORTED)

                if b:
                    self.outputShorted = 1
                else:
                    self.outputShorted = 0

            outputOverloadStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_OUTPUT_OVERLOAD")]
            self.printLog(outputOverloadStatement, "STATUS_OUTPUT_OVERLOAD")
            if outputOverloadStatement is not None and outputOverloadStatement.hasResults:
                b = outputOverloadStatement.results[0] != str(0)

                if b and self.outputOverload != 1:
                    self.occurOnece(self.EventID.ID_UPS_OVERLOAD)

                elif not b and self.outputOverload == 1:
                    self.occurOnece(self.EventID.ID_UPS_OVERLOAD_RESTORE)

                if b:
                    self.outputOverload = 1
                else:
                    self.outputOverload = 0

            overheatStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_INV_OVERHEAT")]
            self.printLog(overheatStatement, "STATUS_INV_OVERHEAT")
            if overheatStatement is not None and overheatStatement.hasResults:
                b = overheatStatement.results[0] != str(0)

                if b and self.overheat != 1:
                    self.occurOnece(self.EventID.ID_SYSTEM_OVERHEAT)

                elif not b and self.overheat == 1:
                    self.occurOnece(self.EventID.ID_SYSTEM_OVERHEAT_RESTORE)

                if b:
                    self.overheat = 1
                else:
                    self.overheat = 0

            batteryExhaustedStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_EXHAUSTED")]
            self.printLog(batteryExhaustedStatement, "STATUS_BATTERY_EXHAUSTED")
            if batteryExhaustedStatement is not None and batteryExhaustedStatement.hasResults:
                b = batteryExhaustedStatement.results[0] != str(0)

                if b and self.batteryExhausted != 1:
                    self.occurOnece(self.EventID.ID_RUNTIME_EXCEED)

                elif not b and self.batteryExhausted == 1:
                    self.occurOnece(self.EventID.ID_RUNTIME_NOT_EXCEED)

                if b:
                    self.batteryExhausted = 1
                else:
                    self.batteryExhausted = 0

            batteryCriticalStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_CRITICAL")]
            self.printLog(batteryCriticalStatement, "STATUS_BATTERY_CRITICAL")
            if batteryCriticalStatement is not None and batteryCriticalStatement.hasResults:
                b = batteryCriticalStatement.results[0] != str(0)

                if b and self.batteryCritical == 0 and self.isUtilityFailure:
                    self.occurOnece(self.EventID.ID_BATTERY_CRITICAL) # check id

                elif not b and self.batteryCritical == 1 and self.isUtilityFailure is False:

                    # because l.b recover only available when p.f recover
                    # so we don't use these code any more.
                    self.occurOnece(self.EventID.ID_BATTERY_CRITICAL_RESTORE) # check id

                if b:
                    self.batteryCritical = 1
                else:
                    self.batteryCritical = 0

            hardwareFaultStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_HARDWARE_FAULT")]
            self.printLog(hardwareFaultStatement, "STATUS_HARDWARE_FAULT")
            if hardwareFaultStatement is not None and hardwareFaultStatement.hasResults:
                b = hardwareFaultStatement.results[0] != str(0)
                # b = True # debug
                if b and self.hardwareFault != 1:

                    self.occurOnece(self.EventID.ID_HARDWARE_FAULT)

                    hardwareFaultCodeStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_FAULT_CODE")]
                    self.printLog(hardwareFaultCodeStatement, "STATUS_FAULT_CODE")

                    # hardwareFaultCodeStatement.results.append("6") # debug
                    # hardwareFaultCodeStatement.results.append("12") # debug
                    if hardwareFaultCodeStatement is not None and hardwareFaultStatement.hasResults:
                        hardwareFaultCode = hardwareFaultCodeStatement.results  # get list
                        Logger.LogIns().logger.info("***[EventAnalyzer] hardwareFaultCode results: {0} ***".format(str(hardwareFaultCode)))

                        f_code_str = ""
                        if len(hardwareFaultCode) > 0:
                            for idx, val in enumerate(hardwareFaultCode):
                                f_code_str += str(val)
                                if (idx + 1) < len(hardwareFaultCode):
                                    f_code_str += ";"

                        stat_f_code_str = str(self.EventID.ID_HARDWARE_FAULT) + "|" + f_code_str

                        Logger.LogIns().logger.info("***[EventAnalyzer] hardwareFaultCode string: {0} ***".format(stat_f_code_str))
                        self.device.eventStatData.append(stat_f_code_str)

                elif not b and self.hardwareFault == 1:

                    self.occurOnece(self.EventID.ID_HARDWARE_FAULT_RESTORE)

                if b:
                    self.hardwareFault = 1
                else:
                    self.hardwareFault = 0

            batteryExpiredProp = self.device.devicePropData.batteryExpired
            if batteryExpiredProp.available:
                batteryNeedReplaceStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BATTERY_REPLACE")]
                self.printLog(batteryNeedReplaceStatement, "STATUS_BATTERY_REPLACE")
                if batteryNeedReplaceStatement is not None and batteryNeedReplaceStatement.hasResults:
                    isBattExpired = batteryNeedReplaceStatement.results[0] != str(0)

                    Logger.LogIns().logger.info("***[EventAnalyzer] isBattExpired value = {0} ***".format(str(isBattExpired)))
                    Logger.LogIns().logger.info("***[EventAnalyzer] isBattNeedReplaced value = {0} ***".format(str(self.device.dataSource.configurationSetting.isBattNeedReplaced)))

                    if isBattExpired:
                        if self.batteryNeedReplaceAlert is False:
                            self.occurOnece(self.EventID.ID_BATTERY_NEED_REPLACE)  # Event occured only onece when daemon started.
                            self.batteryNeedReplaceAlert = True
                            config = Configuration()
                            config.isBattNeedReplaced = True
                            self.device.dataSource.updateDeviceConfig(config)
                    else:
                        if self.device.dataSource.configurationSetting.isBattNeedReplaced:
                            self.occurOnece(self.EventID.ID_BATTERY_REPLACED)

                            config = Configuration()
                            config.isBattNeedReplaced = False
                            self.device.dataSource.updateDeviceConfig(config)

            # else:
            #     batteryLifeSpanMonthProp = self.devicePropData.batteryLifeSpanMonth
            #     if batteryLifeSpanMonthProp.available:
            #         year = batteryLifeSpanMonthProp.value / 12
            #         month = batteryLifeSpanMonthProp.value % 12



            # --------------------------------pre data process--------------------------------

            preEnterECOMode = -1  # 0:false, 1:true, -1:unavailable
            preBypassActive = -1  # 0:false, 1:true, -1:unavailable
            preBypassOverload = -1  # 0:false, 1:true, -1:unavailable
            preWiringFaultActive = -1  # 0:false, 1:true, -1:unavailable
            oldBatteryCharging = -1  # 0:false, 1:true, -1:unavailable
            oldBatteryFullyCharged = -1  # 0:false, 1:true, -1:unavailable

            if self.lastTrxData is not None:
                ltrx = self.lastTrxData

                outputECOModeStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_ECO_MODE")]
                self.printLog(outputECOModeStatement, "STATUS_ECO_MODE")
                if outputECOModeStatement is not None and outputECOModeStatement.hasResults:
                    outputECOMode = outputECOModeStatement.results[0] != str(0)

                    if outputECOMode and self.device.bypassEventCount.isEnterECOModeOccur() == 1:
                        preEnterECOMode = 1
                    else:
                        preEnterECOMode = 0

                bypassActiveStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BYPASS_ACTIVE")]
                self.printLog(bypassActiveStatement, "STATUS_BYPASS_ACTIVE")
                if bypassActiveStatement is not None and bypassActiveStatement.hasResults:
                    bypassActive = bypassActiveStatement.results[0] != str(0)

                    if bypassActive and self.device.bypassEventCount.isBypassActiveOccur() == 1:
                        preBypassActive = 1
                    else:
                        preBypassActive = 0

                bypassOverloadStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BYPASS_OVERLOAD")]
                self.printLog(bypassOverloadStatement, "STATUS_BYPASS_OVERLOAD")
                if bypassOverloadStatement is not None and bypassOverloadStatement.hasResults:
                    bypassOverload = bypassOverloadStatement.results[0] != str(0)

                    if bypassOverload:
                        preBypassOverload = 1
                    else:
                        preBypassOverload = 0

                utilityWiringFaultStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_WIRING_FAULT")]
                self.printLog(utilityWiringFaultStatement, "STATUS_WIRING_FAULT")
                if utilityWiringFaultStatement is not None and utilityWiringFaultStatement.hasResults:
                    utilityWiringFault = utilityWiringFaultStatement.results[0] != str(0)

                    if utilityWiringFault:
                        preWiringFaultActive = 1
                    else:
                        preWiringFaultActive = 0

                batteryChargingStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_CHARGING")]
                self.printLog(batteryChargingStatement, "STATUS_CHARGING")
                if batteryChargingStatement is not None and batteryChargingStatement.hasResults:
                    batteryCharging = batteryChargingStatement.results[0] != str(0)

                    if batteryCharging:
                        oldBatteryCharging = 1
                    else:
                        oldBatteryCharging = 0

                batteryFullChargedStatement = ltrx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_FULL_CHARGED")]
                self.printLog(batteryFullChargedStatement, "STATUS_FULL_CHARGED")
                if batteryFullChargedStatement is not None and batteryFullChargedStatement.hasResults:
                    batteryFullCharged = batteryFullChargedStatement.results[0] != str(0)

                    if batteryFullCharged:
                        oldBatteryFullyCharged = 1
                    else:
                        oldBatteryFullyCharged = 0

            # --------------------------------post data process--------------------------------

            postEnterECOMode = -1  # 0:false, 1:true, -1:unavailable
            postBypassActive = -1  # 0:false, 1:true, -1:unavailable
            postBypassOverload = -1  # 0:false, 1:true, -1:unavailable
            postWiringFaultActive = -1  # 0:false, 1:true, -1:unavailable

            # priority: eco mode -> bypass
            # eco mode
            outputECOModeStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_ECO_MODE")]
            self.printLog(outputECOModeStatement, "STATUS_ECO_MODE")
            if outputECOModeStatement is not None and outputECOModeStatement.hasResults:
                outputECOMode = outputECOModeStatement.results[0] != str(0)

                if outputECOMode:
                    val = 1
                else:
                    val = 0

                postEnterECOMode = self.device.bypassEventCount.checkECOMode(val)

            # compare last time value and now value
            if preEnterECOMode != 1 and postEnterECOMode == 1:  # occur
                self.occurOnece(self.EventID.ID_ENTER_ECO_MODE)
            elif preEnterECOMode == 1 and postEnterECOMode != 1:  # occur
                self.occurOnece(self.EventID.ID_LEAVE_ECO_MODE)

            # bypass active
            bypassActiveStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BYPASS_ACTIVE")]
            self.printLog(bypassActiveStatement, "STATUS_BYPASS_ACTIVE")
            if bypassActiveStatement is not None and bypassActiveStatement.hasResults:
                bypassActive = bypassActiveStatement.results[0] != str(0)

                if bypassActive:
                    val = 1
                else:
                    val = 0

                postBypassActive = self.device.bypassEventCount.checkBypassActive(val)

            # compare last time value and now value
            if preBypassActive != 1 and postBypassActive == 1:  # occur
                self.occurOnece(self.EventID.ID_UPS_BYPASS)

            elif preBypassActive == 1 and postBypassActive != 1:  # occur
                self.occurOnece(self.EventID.ID_UPS_BYPASS_RESTORE)

            # bypass overload
            bypassOverloadStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_BYPASS_OVERLOAD")]
            self.printLog(bypassOverloadStatement, "STATUS_BYPASS_OVERLOAD")
            if bypassOverloadStatement is not None and bypassOverloadStatement.hasResults:
                bypassOverload = bypassOverloadStatement.results[0] != str(0)

                if bypassOverload:
                    postBypassOverload = 1
                else:
                    postBypassOverload = 0

            # compare last time value and now value
            if preBypassOverload != 1 and postBypassOverload == 1:  # occur
                self.occurOnece(self.EventID.ID_BYPASS_OVERLAD)

            elif preBypassOverload == 1 and postBypassOverload != 1:  # occur
                self.occurOnece(self.EventID.ID_BYPASS_OVERLAD_RESTORE)

            # check wiring fault state
            utilityWiringFaultStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_WIRING_FAULT")]
            self.printLog(utilityWiringFaultStatement, "STATUS_WIRING_FAULT")
            if utilityWiringFaultStatement is not None and utilityWiringFaultStatement.hasResults:
                utilityWiringFault = utilityWiringFaultStatement.results[0] != str(0)

                if utilityWiringFault:
                    postWiringFaultActive = 1
                else:
                    postWiringFaultActive = 0

            # compare last time value and now value
            if preWiringFaultActive != 1 and postWiringFaultActive == 1:  # occur
                self.occurOnece(self.EventID.ID_WIRING_FAULT)

            elif preWiringFaultActive == 1 and postWiringFaultActive != 1:  # occur
                self.occurOnece(self.EventID.ID_WIRING_FAULT_RESTORE)

            # battery Fully Charged
            batteryFullChargedStatement = trx.statementsDic[ValueId.ValueIdFinder().getValueId("STATUS_FULL_CHARGED")]
            self.printLog(batteryFullChargedStatement, "STATUS_FULL_CHARGED")
            if batteryFullChargedStatement is not None and batteryFullChargedStatement.hasResults:
                batteryFullCharged = batteryFullChargedStatement.results[0] != str(0)

                if batteryFullCharged:
                    self.batteryFullyCharged = 1
                else:
                    self.batteryFullyCharged = 0

            # 前次status電池處於充電中, 但未充滿, 而本次status電池已充滿
            if self.batteryFullyCharged == 1 and oldBatteryCharging == 1 and oldBatteryFullyCharged == 0:  # occur
                self.occurOnece(self.EventID.ID_BATTERY_CHARGED_FULLY)


            self.analyzeEventCode(deviceStatus)
            self.lastTrxData = trx  # save now value to last time value
            self.printFlag(False)

            # 實作關機
            print("isUtilityFailure: " + str(self.isUtilityFailure))
            if self.isUtilityFailure:
                Logger.LogIns().logger.info("***[EventAnalyzer] Into decideShutdownAction() ***")
                self.decideShutdownAction(deviceStatus)

        except Exception as e:
            Logger.LogIns().logger.info(e)
            Logger.LogIns().logger.error(traceback.format_exc())

    def restartShutdownAction(self):
        if self.schedulerManager.isShutdownExcuting:
            self.isReConfig = True
        self.schedulerManager.stopShutdownSchedule()

    def decideShutdownAction(self, deviceStatus):

        config = DataSource2.DataSource2().readActiveConfig()

        delayTime = int(config.runtimeCountdownTime)  # unit: minutes

        configData = self.deviceConfigure.configParam()
        configData.CMD_SLEEP = 1
        configData.params.append(settings.shutdownDuration)  # 倒數完 + 2分鐘後UPS關機(避免電腦早於UPS關機)
        shutdownUtil = ShutdownUtil.ShutdownUtil(config.shutDownType, configData, self.device.desktopInteractiveServer, self.device.deviceId, self)


        if config is not None and config.runtimeType == ViewData.RuntimeSettingEnum.PreserveBatteryPower.value:
            # isShutdown: 為必免重複觸發只有在occur event時會設為true
            # isReConfig: 當使用者修改runtime設定後，就會設為true以重新執行此關機行為
            if (self.isShutdown or self.isReConfig):
            # 當滿足關機條件時，只會判斷是否設定為Preserve Battery Power，若是此設定就會開始進行關機的行為
                delayTime = delayTime * 60  # convert minute to second
                print("do shutdown thread")
                self.schedulerManager.addShutdownSchedule(Scheduler.ShutdownThread("ShutdownThread", delayTime, shutdownUtil))
                self.schedulerManager.startShutdownSchedule()

        elif config is not None and config.runtimeType == ViewData.RuntimeSettingEnum.KeepComputerRunning.value:
            if deviceStatus.RuntimeLow is not None and deviceStatus.RuntimeLow:
                self.schedulerManager.addShutdownSchedule(Scheduler.ShutdownThread("ShutdownThread", 0, shutdownUtil))
                self.schedulerManager.startShutdownSchedule()

        self.isReConfig = False

    def occur(self, eventId):
        try:
            Logger.LogIns().logger.info("***[EventAnalyzer] occur() eventId value: {0} ***".format(str(eventId.value)))

            # check event occur already
            if eventId in self.eventOccuredRecord:
                print(str(eventId) + "occur already")

            else:
                self.device.devicePushAlertMsg.messageTitle = self.device.customUPSName

                if eventId.value == self.EventID.ID_UTILITY_FAILURE.value:
                    # todo shutdown
                    # todo software sounds
                    self.isShutdown = True
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_FAILURE.name

                if eventId.value == self.EventID.ID_COMMUNICATION_LOST.value:
                    print("communication lost")
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_COMMUNICATION_LOST.name

                if eventId.value == self.EventID.ID_UTILITY_TRANSFER_HIGH.value:
                    # todo shutdown
                    # todo software sounds
                    self.isShutdown = True
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_TRANSFER_HIGH.name

                if eventId.value == self.EventID.ID_UTILITY_TRANSFER_LOW.value:
                    # todo shutdown
                    # todo software sounds
                    self.isShutdown = True
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_TRANSFER_LOW.name

                if eventId.value == self.EventID.ID_AVR_BOOST_ACTIVE.value:
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_AVR_BOOST_ACTIVE.name

                if eventId.value == self.EventID.ID_AVR_BUCK_ACTIVE.value:
                    self.device.devicePushAlertMsg.messageBody = self.EventID.ID_AVR_BUCK_ACTIVE.name

                self.device.cloudEvents.append(eventId.value)
                self.dataSource.addAnEventLog(str(eventId.value), 0)  # insert an event log in db

                if self.dataSource.emailNotification is not None and self.dataSource.emailNotification.active:
                    self.schedulerManager.addSendMailSchedule(
                        Scheduler.SendMailThread("SendMailThread", self.dataSource.emailNotification,
                                                 self.dataSource.oauthCredentials, eventId, False))
                    self.schedulerManager.startSendMailSchedule()

                # config = DataSource2.DataSource2().readActiveConfig()
                # if config is not None and config.softwareSoundEnable:
                #     # do beeper
                #     OSOperator.OSOperator().doBeep()

                self.eventOccuredRecord.append(eventId)

            print("self.eventOccuredRecord" + str(self.eventOccuredRecord))
            Logger.LogIns().logger.info("***[EventAnalyzer] restoreOccur() eventOccuredRecord value = {0} ***".format(str(self.eventOccuredRecord)))

        except Exception as e:
            Logger.LogIns().logger.info(e)
            Logger.LogIns().logger.error(traceback.format_exc())

    def restoreOccur(self, eventId):
        try:
            Logger.LogIns().logger.info("[EventAnalyzer] eventId: " + str(eventId.value))
            Logger.LogIns().logger.info("[EventAnalyzer] eventOccuredRecord: " + str(self.eventOccuredRecord))

            needSendMail = False  # this flag is a bad solution, maybe refactor it later
            self.device.devicePushAlertMsg.messageTitle = self.device.customUPSName

            if eventId is not None and eventId.value is not None:

                needInsertEvent = False
                if eventId.value == self.EventID.ID_UTILITY_FAILURE_RESTORE.value \
                        or eventId.value == self.EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE.value \
                        or eventId.value == self.EventID.ID_UTILITY_TRANSFER_LOW_RESTORE.value:

                    # restore failure
                    if self.EventID.ID_UTILITY_FAILURE in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.outputStopSoon = 0
                        self.eventOccuredRecord.remove(self.EventID.ID_UTILITY_FAILURE)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_UTILITY_FAILURE.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_UTILITY_FAILURE_RESTORE.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_FAILURE_RESTORE.name
                        self.device.cloudEvents.append(self.EventID.ID_UTILITY_FAILURE_RESTORE.value)

                    if self.EventID.ID_UTILITY_TRANSFER_HIGH in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.eventOccuredRecord.remove(self.EventID.ID_UTILITY_TRANSFER_HIGH)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_UTILITY_TRANSFER_HIGH.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE.name
                        self.device.cloudEvents.append(self.EventID.ID_UTILITY_TRANSFER_HIGH_RESTORE.value)

                    if self.EventID.ID_UTILITY_TRANSFER_LOW in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.eventOccuredRecord.remove(self.EventID.ID_UTILITY_TRANSFER_LOW)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_UTILITY_TRANSFER_LOW.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_UTILITY_TRANSFER_LOW_RESTORE.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_UTILITY_TRANSFER_LOW_RESTORE.name
                        self.device.cloudEvents.append(self.EventID.ID_UTILITY_TRANSFER_LOW_RESTORE.value)

                    self.schedulerManager.stopShutdownSchedule()

                if eventId.value == self.EventID.ID_COMMUNICATION_ESTABLISHED.value:

                    if self.EventID.ID_COMMUNICATION_LOST in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.eventOccuredRecord.remove(self.EventID.ID_COMMUNICATION_LOST)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_COMMUNICATION_LOST.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_COMMUNICATION_ESTABLISHED.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_COMMUNICATION_ESTABLISHED.name
                        self.device.cloudEvents.append(self.EventID.ID_COMMUNICATION_ESTABLISHED.value)

                if eventId.value == self.EventID.ID_AVR_BOOST_RESTORE.value:

                    if self.EventID.ID_AVR_BOOST_ACTIVE in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.eventOccuredRecord.remove(self.EventID.ID_AVR_BOOST_ACTIVE)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_AVR_BOOST_ACTIVE.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_AVR_BOOST_RESTORE.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_AVR_BOOST_RESTORE.name
                        self.device.cloudEvents.append(self.EventID.ID_AVR_BOOST_RESTORE.value)

                if eventId.value == self.EventID.ID_AVR_BUCK_RESTORE.value:

                    if self.EventID.ID_AVR_BUCK_ACTIVE in self.eventOccuredRecord:
                        needSendMail = True
                        needInsertEvent = True
                        self.eventOccuredRecord.remove(self.EventID.ID_AVR_BUCK_ACTIVE)
                        self.dataSource.updateEventLogDuration(self.EventID.ID_AVR_BUCK_ACTIVE.value)

                        # self.device.devicePushSilenceMsg.Event = self.EventMoble.GetEventObj(self.EventID.ID_AVR_BUCK_RESTORE.name)
                        self.device.devicePushAlertMsg.messageBody = self.EventID.ID_AVR_BUCK_RESTORE.name
                        self.device.cloudEvents.append(self.EventID.ID_AVR_BUCK_RESTORE.value)

                # if self.device.devicePushAlertMsg.messageTitle is not None and self.device.devicePushAlertMsg.messageBody is not None:
                #     self.fcmProvider.doSendApnsAlertMsg()
                #     self.device.devicePushAlertMsg = DevicePushMessageData.AlertMessage()  # clear

                    # self.EmqMsgProvider.doSendEmqStatusMsg()  # 帶event之封包僅送一次
                    # self.device.devicePushSilenceMsg.Event = DevicePushMessageData.SilenceMessage.Event()  # clear

                if needInsertEvent:
                    self.dataSource.addAnEventLog(str(eventId.value), 0)  # insert restore event

            if needSendMail and self.dataSource.emailNotification is not None and self.dataSource.emailNotification.active:
                self.schedulerManager.addSendMailSchedule(
                    Scheduler.SendMailThread("SendMailThread", self.dataSource.emailNotification,
                                             self.dataSource.oauthCredentials, eventId, False))
                self.schedulerManager.startSendMailSchedule()

            print("restore self.eventOccuredRecord" + str(self.eventOccuredRecord))
            Logger.LogIns().logger.info("***[EventAnalyzer] restoreOccur() eventOccuredRecord value = {0} ***".format(str(self.eventOccuredRecord)))

        except Exception as e:
            Logger.LogIns().logger.info(e)
            Logger.LogIns().logger.error(traceback.format_exc())

    def occurOnece(self, eventId, isHwFault= None, levelCode= None, errorCode= None):
        try:
            pairedEvent = [
                self.EventID.ID_UTILITY_FAILURE.value,
                self.EventID.ID_COMMUNICATION_LOST.value,
                self.EventID.ID_UTILITY_TRANSFER_HIGH.value,
                self.EventID.ID_UTILITY_TRANSFER_LOW.value,
                self.EventID.ID_AVR_BOOST_ACTIVE.value,
                self.EventID.ID_AVR_BUCK_ACTIVE.value
            ]

            if eventId.value not in pairedEvent:

                self.device.cloudEvents.append(eventId.value)
                self.dataSource.addAnEventLog(str(eventId.value), 0, isHwFault, levelCode, errorCode)  # insert an event log in db
                print("insert an event log done")

                if self.dataSource.emailNotification is not None and self.dataSource.emailNotification.active:
                    self.schedulerManager.addSendMailSchedule(Scheduler.SendMailThread("SendMailThread", self.dataSource.emailNotification, self.dataSource.oauthCredentials, eventId, False, isHwFault=isHwFault, errorCode=errorCode))
                    self.schedulerManager.startSendMailSchedule()

            print("occurOnece() eventId value = {0} " + str(eventId.value))
            Logger.LogIns().logger.info("***[EventAnalyzer] occurOnece() eventId value = {0} ***".format(str(eventId.value)))

        except Exception as e:
            Logger.LogIns().logger.info(e)
            Logger.LogIns().logger.error(traceback.format_exc())

    def setEnterHibernation(self, shutdownType):
        if int(shutdownType) == ViewData.ShutdownTypeEnum.Hibernation.value:
            self.device.enterHibernation = True

    def printLog(self, stat, ValueId):
        try:
            f1 = True
            if stat is None:
                Logger.LogIns().logger.info("***[EventAnalyzer] stat: {0} is None ***".format(ValueId))
                f1 = False

            f2 = True
            if not stat.hasResults:
                Logger.LogIns().logger.info("***[EventAnalyzer] stat: {0} not hasResults ***".format(ValueId))
                f2 = False

            if f1 and f2:
                Logger.LogIns().logger.info("***[EventAnalyzer] stat: {0} value = {1} ***".format(ValueId, str(stat.results)))

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def printFlag(self, titleFlag):
        try:
            keyList = [
                "isUtilityFailure",
                "isReConfig",
                "batteryCharging",
                "batteryDischarging",
                "batteryNotPresent",
                "outputShorted",
                "outputOverload",
                "overheat",
                "batteryExhausted",
                "batteryCritical",
                "hardwareFault",
                "batteryTesting",
                "batteryFullyCharged",
                "eventOccuredRecord",
                "cloudEvents",
                "batteryNeedReplaceAlert",
                "eventStatData"
            ]

            valList = [
                self.isUtilityFailure,
                self.isReConfig,
                self.batteryCharging,
                self.batteryDischarging,
                self.batteryNotPresent,
                self.outputShorted,
                self.outputOverload,
                self.overheat,
                self.batteryExhausted,
                self.batteryCritical,
                self.hardwareFault,
                self.batteryTesting,
                self.batteryFullyCharged,
                self.eventOccuredRecord,
                self.device.cloudEvents,
                self.batteryNeedReplaceAlert,
                self.device.eventStatData
            ]

            if titleFlag:
                Logger.LogIns().logger.info("***[EventAnalyzer] START ANALYZE ***")
            else:
                Logger.LogIns().logger.info("***[EventAnalyzer] END ANALYZE ***")

            for i, f in enumerate(valList):
                if keyList[i] in ["eventOccuredRecord", "cloudEvents"]:
                    if f is not None and len(f) > 0:
                        val = "[" + ','.join(str(p) for p in f) + "]"
                    else:
                        val = "[]"
                else:
                    val = str(f)

                Logger.LogIns().logger.info("***[EventAnalyzer] flag: {0} value = {1} ***".format(keyList[i], val))

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def checkThreadComplete(self):
        Logger.LogIns().logger.info("***[EventAnalyzer] begin sleep***")
        time.sleep(6)

        Logger.LogIns().logger.info("***[EventAnalyzer] begin check thread complete***")
        Logger.LogIns().logger.info("***[EventAnalyzer] emqMsgThreadPool length: {0} ***".format(str(len(self.schedulerManager.emqMsgThreadPool))))
        Logger.LogIns().logger.info("***[EventAnalyzer] deviceLogThreadPool length: {0} ***".format(str(len(self.schedulerManager.deviceLogThreadPool))))

        f1 = self.schedulerManager.checkDeviceLogThreadComplete()
        f2 = self.schedulerManager.checkEmqMsgThreadComplete()

        Logger.LogIns().logger.info("***[EventAnalyzer] f1 flag: {0} ***".format(str(f1)))
        Logger.LogIns().logger.info("***[EventAnalyzer] f2 flag: {0} ***".format(str(f2)))

    def sendShutdownEvent(self):
        self.outputStopSoon = 1
        self.occurOnece(self.EventID.ID_OUTPUT_STOP_SOON)

        if platform.system() == 'Darwin':
           self.occur(self.EventID.ID_COMMUNICATION_LOST)

        self.WebAppController.saveAndSendDeviceLog(False)

    def analyzeEventCode(self, deviceStatus):

        try:
            if isinstance(deviceStatus.UpsEventCode, list) and isinstance(self.lastUpsEventCode, list):
                self.eventCodeRestore = list(set(self.lastUpsEventCode) - set(deviceStatus.UpsEventCode))
                self.eventCodeNew = list(set(deviceStatus.UpsEventCode) - set(self.lastUpsEventCode))

                if len(deviceStatus.UpsEventCode) >0:
                    self.device.devicePushSilenceMsg.EventCode = ';'.join(map(str, deviceStatus.UpsEventCode))

                if len(self.eventCodeRestore) >0:
                    for k,v in enumerate(self.eventCodeRestore):
                        if "." in v:
                            level_code = v.split(".")[1]  # ex: 0,1...
                            err_code = v.split(".")[0]  # ex: C63, C52, U2...
                            self.occurOnece(self.EventID.ID_HARDWARE_STATUS_RESTORE, True, level_code, err_code)

                    self.device.devicePushSilenceMsg.EventCodeRestore = ';'.join(map(str, self.eventCodeRestore))

                if len(self.eventCodeNew) >0:
                    for k,v in enumerate(self.eventCodeNew):
                        if "." in v:
                            level_code = v.split(".")[1]  # ex: 0,1...
                            err_code = v.split(".")[0]  # ex: C63, C52, U2...
                            self.occurOnece(self.EventID.ID_HARDWARE_STATUS, True, level_code, err_code)

                    self.device.devicePushSilenceMsg.EventCodeNew = ';'.join(map(str, self.eventCodeNew))

            self.lastUpsEventCode = deviceStatus.UpsEventCode  # save last data

        except Exception as e:
            Logger.LogIns().logger.info(e)
            Logger.LogIns().logger.error(traceback.format_exc())




