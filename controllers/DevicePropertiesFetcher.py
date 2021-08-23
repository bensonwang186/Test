import sys
import traceback

from PyQt5.QtCore import QObject, pyqtSignal

from System import ValueId
from model_Json import Transaction, Statement
from Utility import Logger


class DeviceProperties(QObject):
    propertySignal = pyqtSignal(object)
    noFetchSignal = pyqtSignal(object)
    # sendEmqStatusMsgSignal = pyqtSignal(int)
    mobileLoginSignal = pyqtSignal(int)

    def __init__(self, propData):
        super(DeviceProperties, self).__init__()
        self.devicePropData = propData
        self.propertyId = dict()
        self.buildPropertyId()



    """取得Device屬性"""

    def buildPropertyId(self):
        valueIdFinder = ValueId.ValueIdFinder()

        self.propertyId[valueIdFinder.getValueId("PROP_BUZZER_ALLOW")] = self.devicePropData.upsAlarmEnable
        self.propertyId[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW")] = self.devicePropData.lowerLimitProperty
        self.propertyId[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW")] = self.devicePropData.lowerLimitList
        self.propertyId[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH")] = self.devicePropData.upperLimitProperty
        self.propertyId[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH")] = self.devicePropData.upperLimitList
        self.propertyId[valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY")] = self.devicePropData.sensitivity
        self.propertyId[valueIdFinder.getValueId("PROP_MODEL_NAME")] = self.devicePropData.modelName
        self.propertyId[valueIdFinder.getValueId("PROP_HARDWARE_VERSION")] = self.devicePropData.firmwareVer
        self.propertyId[valueIdFinder.getValueId("PROP_ACTIVE_POWER")] = self.devicePropData.activePower
        self.propertyId[valueIdFinder.getValueId("PROP_APPARENT_POWER")] = self.devicePropData.apparentPower
        self.propertyId[valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")] = self.devicePropData.cumulativeEnergyConsumption
        self.propertyId[valueIdFinder.getValueId("PROP_SERIAL_NUMBER")] = self.devicePropData.serialNumber
        self.propertyId[valueIdFinder.getValueId("PROP_BATTERY_LIFE_SPAN_MONTH")] = self.devicePropData.batteryLifeSpanMonth
        self.propertyId[valueIdFinder.getValueId("STATUS_BATTERY_REPLACE")] = self.devicePropData.batteryExpired
        self.propertyId[valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD")] = self.devicePropData.batteryRuntime
        self.propertyId[valueIdFinder.getValueId("PROP_LIST_BATTERY_RUNTIME_THRESHOLD")] = self.devicePropData.batteryRuntimeRange
        self.propertyId[valueIdFinder.getValueId("PROP_UPS_EVENT_CODE")] = self.devicePropData.upsEventCode

    def noFetchProperties(self):
        self.noFetchSignal.emit(self)

    def fetchAllProperties(self, helper, deviceId):
        trx = Transaction.Transaction()
        trx.setDeviceId(deviceId)

        valueIdFinder = ValueId.ValueIdFinder()
        buzzerAllowStatement = Statement.Statement(valueIdFinder.getValueId("PROP_BUZZER_ALLOW"))
        lowTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW"))
        listLowTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW"))
        highTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH"))
        listHighTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH"))
        batteryTestingStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_TESTING"))
        hardwareFaultStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_HARDWARE_FAULT"))
        voltSensitivityStatement = Statement.Statement(valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY"))
        modelNameStatement = Statement.Statement(valueIdFinder.getValueId("PROP_MODEL_NAME"))
        hardwareVersionStatement = Statement.Statement(valueIdFinder.getValueId("PROP_HARDWARE_VERSION"))
        activePowerStatement = Statement.Statement(valueIdFinder.getValueId("PROP_ACTIVE_POWER"))
        apparentPowerStatement = Statement.Statement(valueIdFinder.getValueId("PROP_APPARENT_POWER"))
        cumulativeEnergyConsumptionStatement = Statement.Statement(valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION"))
        voltRatingStatement = Statement.Statement(valueIdFinder.getValueId("PROP_RATING_VOLT"))
        snStatement = Statement.Statement(valueIdFinder.getValueId("PROP_SERIAL_NUMBER"))
        batteryLifeSpanMonthStatement = Statement.Statement(valueIdFinder.getValueId("PROP_BATTERY_LIFE_SPAN_MONTH"))
        batteryExpiredStatement = Statement.Statement(valueIdFinder.getValueId("STATUS_BATTERY_REPLACE"))
        batteryRuntimeStatement = Statement.Statement(valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD"))
        batteryRuntimeRangeStatement = Statement.Statement(valueIdFinder.getValueId("PROP_LIST_BATTERY_RUNTIME_THRESHOLD"))
        upsEventCodeStatement = Statement.Statement(valueIdFinder.getValueId("PROP_UPS_EVENT_CODE"))

        trx.add(buzzerAllowStatement)
        trx.add(lowTransferVoltStatement)
        trx.add(listLowTransferVoltStatement)
        trx.add(highTransferVoltStatement)
        trx.add(listHighTransferVoltStatement)
        trx.add(batteryTestingStatement)
        trx.add(hardwareFaultStatement)
        trx.add(voltSensitivityStatement)
        trx.add(modelNameStatement)
        trx.add(hardwareVersionStatement)
        trx.add(activePowerStatement)
        trx.add(apparentPowerStatement)
        trx.add(cumulativeEnergyConsumptionStatement)
        trx.add(voltRatingStatement)
        trx.add(snStatement)
        trx.add(batteryLifeSpanMonthStatement)
        trx.add(batteryExpiredStatement)
        trx.add(batteryRuntimeStatement)
        trx.add(batteryRuntimeRangeStatement)
        trx.add(upsEventCodeStatement)

        try:
            flag = helper.submit(trx)  # Get transaction from device

            valueIdFinder = ValueId.ValueIdFinder()
            if flag is True:
                if valueIdFinder.getValueId("PROP_BUZZER_ALLOW") in trx.statementsDic and trx.statementsDic[valueIdFinder.getValueId("PROP_BUZZER_ALLOW")].hasResults:
                    self.devicePropData.upsAlarmEnable.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_BUZZER_ALLOW")].results[0])
                else:
                    self.devicePropData.upsAlarmEnable.clearAvailable()
                    self.devicePropData.upsAlarmEnable.clearConfigurable()


                if valueIdFinder.getValueId("PROP_MODEL_NAME") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_MODEL_NAME")].hasResults:
                    results = trx.statementsDic[valueIdFinder.getValueId("PROP_MODEL_NAME")].results
                    modelName = ""
                    for i in range(0, len(results)):
                        modelName += results[i]
                    self.devicePropData.modelName.value = modelName
                else:
                    self.devicePropData.modelName.clearAvailable()
                    self.devicePropData.modelName.clearConfigurable()

                if valueIdFinder.getValueId("PROP_HARDWARE_VERSION") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_HARDWARE_VERSION")].hasResults:
                    self.devicePropData.firmwareVer.value = trx.statementsDic[valueIdFinder.getValueId("PROP_HARDWARE_VERSION")].results[0]
                else:
                    self.devicePropData.firmwareVer.clearAvailable()
                    self.devicePropData.firmwareVer.clearConfigurable()

                if valueIdFinder.getValueId("PROP_ACTIVE_POWER") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_ACTIVE_POWER")].hasResults:
                    self.devicePropData.activePower.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_ACTIVE_POWER")].results[0])
                else:
                    self.devicePropData.activePower.clearAvailable()
                    self.devicePropData.activePower.clearConfigurable()

                if valueIdFinder.getValueId("PROP_APPARENT_POWER") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_APPARENT_POWER")].hasResults:
                    self.devicePropData.apparentPower.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_APPARENT_POWER")].results[0])
                else:
                    self.devicePropData.apparentPower.clearAvailable()
                    self.devicePropData.apparentPower.clearConfigurable()

                if valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH")].hasResults:
                    self.devicePropData.upperLimitProperty.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH")].results[0])
                else:
                    self.devicePropData.upperLimitProperty.clearAvailable()
                    self.devicePropData.upperLimitProperty.clearConfigurable()

                if valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW")].hasResults:
                    self.devicePropData.lowerLimitProperty.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW")].results[0])
                else:
                    self.devicePropData.lowerLimitProperty.clearAvailable()
                    self.devicePropData.lowerLimitProperty.clearConfigurable()

                if valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH")].hasResults:
                    highList = []
                    for volt in trx.statementsDic[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH")].results:
                        highList.append(int(volt))
                    self.devicePropData.upperLimitList.value = highList
                else:
                    self.devicePropData.upperLimitList.value = []
                    self.devicePropData.upperLimitList.clearAvailable()
                    self.devicePropData.upperLimitList.clearConfigurable()

                if valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW")].hasResults:
                    lowList = []
                    for volt in trx.statementsDic[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW")].results:
                        lowList.append(int(volt))
                    self.devicePropData.lowerLimitList.value = lowList
                else:
                    self.devicePropData.lowerLimitList.value = []
                    self.devicePropData.lowerLimitList.clearAvailable()
                    self.devicePropData.lowerLimitList.clearConfigurable()

                if valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY")].hasResults:
                    self.devicePropData.sensitivity.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY")].results[0])
                else:
                    self.devicePropData.sensitivity.value = -1
                    self.devicePropData.sensitivity.clearAvailable()
                    self.devicePropData.sensitivity.clearConfigurable()

                if valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].hasResults:
                    self.devicePropData.cumulativeEnergyConsumption.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].results[0])
                else:
                    self.devicePropData.cumulativeEnergyConsumption.clearAvailable()
                    self.devicePropData.cumulativeEnergyConsumption.clearConfigurable()

                if valueIdFinder.getValueId("PROP_RATING_VOLT") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_RATING_VOLT")].hasResults:
                    self.devicePropData.voltRating.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_RATING_VOLT")].results[0])
                else:
                    self.devicePropData.voltRating.clearAvailable()
                    self.devicePropData.voltRating.clearConfigurable()

                if valueIdFinder.getValueId("PROP_SERIAL_NUMBER") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_SERIAL_NUMBER")].hasResults:
                    self.devicePropData.serialNumber.value = trx.statementsDic[valueIdFinder.getValueId("PROP_SERIAL_NUMBER")].results[0]
                else:
                    self.devicePropData.serialNumber.value = ""
                    self.devicePropData.serialNumber.clearAvailable()
                    self.devicePropData.serialNumber.clearConfigurable()

                if valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD")].hasResults:
                    self.devicePropData.batteryRuntime.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD")].results[0])
                else:
                    self.devicePropData.batteryRuntime.clearAvailable()
                    self.devicePropData.batteryRuntime.clearConfigurable()

                if valueIdFinder.getValueId("PROP_LIST_BATTERY_RUNTIME_THRESHOLD") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_LIST_BATTERY_RUNTIME_THRESHOLD")].hasResults:
                    batteryRuntimeRange = []
                    for runtime in trx.statementsDic[valueIdFinder.getValueId("PROP_LIST_BATTERY_RUNTIME_THRESHOLD")].results:
                        batteryRuntimeRange.append(int(runtime))
                    self.devicePropData.batteryRuntimeRange.value = batteryRuntimeRange
                else:
                    self.devicePropData.batteryRuntimeRange.value = []

                # if activePowerStatement.errCode == 0 and activePowerStatement.hasResults:
                #     # with self.activePower.lock:
                #     self.activePower.setAvailable()  # 若機器傳回prop.,則Available設true
                #
                #     if len(activePowerStatement.results) > 0 and systemFunction.intTryParse(
                #             activePowerStatement.results[0]):
                #         self.activePower.setValue(int(activePowerStatement.results[0]))  # 設定value的值
                # else:
                #     self.activePower.clearAvailable()  # 若機器無法傳回prop.,則Available設false

                postBatteryLifeSpanMonthStatement = trx.statementsDic[valueIdFinder.getValueId("PROP_BATTERY_LIFE_SPAN_MONTH")]
                self.printLog(postBatteryLifeSpanMonthStatement, "PROP_BATTERY_LIFE_SPAN_MONTH")
                if postBatteryLifeSpanMonthStatement is not None and postBatteryLifeSpanMonthStatement.hasResults:
                    self.devicePropData.batteryLifeSpanMonth.value = int(postBatteryLifeSpanMonthStatement.results[0])
                    self.devicePropData.batteryLifeSpanMonth.available = True
                else:
                    self.devicePropData.batteryLifeSpanMonth.value = -1
                    self.devicePropData.batteryLifeSpanMonth.clearAvailable()
                    self.devicePropData.batteryLifeSpanMonth.clearConfigurable()

                postBatteryExpiredStatement = trx.statementsDic[valueIdFinder.getValueId("STATUS_BATTERY_REPLACE")]
                self.printLog(postBatteryExpiredStatement, "STATUS_BATTERY_REPLACE")
                if postBatteryExpiredStatement is not None and postBatteryExpiredStatement.hasResults:
                    self.devicePropData.batteryExpired.value = int(postBatteryExpiredStatement.results[0])
                    self.devicePropData.batteryExpired.available = True
                else:
                    self.devicePropData.batteryExpired.value = False
                    self.devicePropData.batteryExpired.clearAvailable()
                    self.devicePropData.batteryExpired.clearConfigurable()

                if valueIdFinder.getValueId("PROP_UPS_EVENT_CODE") in trx.statementsDic and trx.statementsDic[
                    valueIdFinder.getValueId("PROP_UPS_EVENT_CODE")].hasResults:
                    self.devicePropData.upsEventCode.value = trx.statementsDic[valueIdFinder.getValueId("PROP_UPS_EVENT_CODE")].results
                else:
                    self.devicePropData.upsEventCode.value = ""
                    self.devicePropData.upsEventCode.clearAvailable()
                    self.devicePropData.upsEventCode.clearConfigurable()

            self.deviceId = trx.deviceId
            self.propertySignal.emit(self)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
        #self.propertySignal.emit(trx)
        return True

    def updateProperties(self, helper, deviceId, changeId):
        trx = Transaction.Transaction()
        trx.setDeviceId(deviceId)

        valueIdFinder = ValueId.ValueIdFinder()
        configChangePropertyStatement = Statement.Statement(valueIdFinder.getValueId("PROP_CONFIG_CHANGE"))
        configChangePropertyStatement.params.append(changeId)

        trx.add(configChangePropertyStatement)

        flag = helper.submit(trx)  # Get transaction from device

        if configChangePropertyStatement.errCode == 0 and configChangePropertyStatement.hasResults:
            resultList = configChangePropertyStatement.results
            for proId in resultList:
                if int(proId) in self.propertyId.keys():
                    self.propertyId[int(proId)].setChanged()

    def fetchChangedProperties(self, helper, deviceId):
        trx = Transaction.Transaction()
        trx.setDeviceId(deviceId)

        valueIdFinder = ValueId.ValueIdFinder()
        buzzerAllowStatement = Statement.Statement(valueIdFinder.getValueId("PROP_BUZZER_ALLOW"))
        lowTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW"))
        listLowTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW"))
        highTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH"))
        listHighTransferVoltStatement = Statement.Statement(valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH"))
        voltSensitivityStatement = Statement.Statement(valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY"))
        modelNameStatement = Statement.Statement(valueIdFinder.getValueId("PROP_MODEL_NAME"))
        hardwareVersionStatement = Statement.Statement(valueIdFinder.getValueId("PROP_HARDWARE_VERSION"))
        activePowerStatement = Statement.Statement(valueIdFinder.getValueId("PROP_ACTIVE_POWER"))
        apparentPowerStatement = Statement.Statement(valueIdFinder.getValueId("PROP_APPARENT_POWER"))
        cumulativeEnergyConsumptionStatement = Statement.Statement(valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION"))
        voltRatingStatement = Statement.Statement(valueIdFinder.getValueId("PROP_RATING_VOLT"))
        snStatement = Statement.Statement(valueIdFinder.getValueId("PROP_SERIAL_NUMBER"))
        batteryRuntimeStatement = Statement.Statement(valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD"))
        upsEventCodeStatement = Statement.Statement(valueIdFinder.getValueId("PROP_UPS_EVENT_CODE"))

        Logger.LogIns().logger.info("***[PropFetcher] upsAlarmEnable isChanged: {0} ***".format(str(self.devicePropData.upsAlarmEnable.isChanged())))
        if self.devicePropData.upsAlarmEnable.isChanged():
            trx.add(buzzerAllowStatement)

        Logger.LogIns().logger.info("***[PropFetcher] lowerLimitList isChanged: {0} ***".format(str(self.devicePropData.lowerLimitList.isChanged())))
        if self.devicePropData.lowerLimitList.isChanged():
            trx.add(listLowTransferVoltStatement)

        Logger.LogIns().logger.info("***[PropFetcher] lowerLimitProperty isChanged: {0} ***".format(str(self.devicePropData.lowerLimitProperty.isChanged())))
        if self.devicePropData.lowerLimitProperty.isChanged():
            trx.add(lowTransferVoltStatement)

        Logger.LogIns().logger.info("***[PropFetcher] upperLimitList isChanged: {0} ***".format(str(self.devicePropData.upperLimitList.isChanged())))
        if self.devicePropData.upperLimitList.isChanged():
            trx.add(listHighTransferVoltStatement)

        Logger.LogIns().logger.info("***[PropFetcher] upperLimitProperty isChanged: {0} ***".format(str(self.devicePropData.upperLimitProperty.isChanged())))
        if self.devicePropData.upperLimitProperty.isChanged():
            trx.add(highTransferVoltStatement)

        Logger.LogIns().logger.info("***[PropFetcher] sensitivity isChanged: {0} ***".format(str(self.devicePropData.sensitivity.isChanged())))
        if self.devicePropData.sensitivity.isChanged():
            trx.add(voltSensitivityStatement)

        Logger.LogIns().logger.info("***[PropFetcher] modelName isChanged: {0} ***".format(str(self.devicePropData.modelName.isChanged())))
        if self.devicePropData.modelName.isChanged():
            trx.add(modelNameStatement)

        Logger.LogIns().logger.info("***[PropFetcher] firmwareVer isChanged: {0} ***".format(str(self.devicePropData.firmwareVer.isChanged())))
        if self.devicePropData.firmwareVer.isChanged():
            trx.add(hardwareVersionStatement)

        Logger.LogIns().logger.info("***[PropFetcher] activePower isChanged: {0} ***".format(str(self.devicePropData.activePower.isChanged())))
        if self.devicePropData.activePower.isChanged():
            trx.add(activePowerStatement)

        Logger.LogIns().logger.info("***[PropFetcher] apparentPower isChanged: {0} ***".format(str(self.devicePropData.apparentPower.isChanged())))
        if self.devicePropData.apparentPower.isChanged():
            trx.add(apparentPowerStatement)

        Logger.LogIns().logger.info("***[PropFetcher] cumulativeEnergyConsumption isChanged: {0} ***".format(str(self.devicePropData.cumulativeEnergyConsumption.isChanged())))
        if self.devicePropData.cumulativeEnergyConsumption.isChanged():
            trx.add(cumulativeEnergyConsumptionStatement)

        Logger.LogIns().logger.info("***[PropFetcher] voltRating isChanged: {0} ***".format(str(self.devicePropData.voltRating.isChanged())))
        if self.devicePropData.voltRating.isChanged():
            trx.add(voltRatingStatement)

        Logger.LogIns().logger.info("***[PropFetcher] batteryRuntime isChanged: {0} ***".format(str(self.devicePropData.batteryRuntime.isChanged())))
        if self.devicePropData.batteryRuntime.isChanged():
            trx.add(batteryRuntimeStatement)

        Logger.LogIns().logger.info("***[PropFetcher] SN isChanged: {0} ***".format(str(self.devicePropData.serialNumber.isChanged())))
        if self.devicePropData.serialNumber.isChanged():
            trx.add(snStatement)

        Logger.LogIns().logger.info("***[PropFetcher] SN upsEventCode: {0} ***".format(str(self.devicePropData.upsEventCode.isChanged())))
        if self.devicePropData.upsEventCode.isChanged():
            trx.add(upsEventCodeStatement)


        flag = helper.submit(trx)  # Get transaction from device
        valueIdFinder = ValueId.ValueIdFinder()
        Logger.LogIns().logger.info("***[PropFetcher] transaction flag checked: {0} ***".format(str(flag)))
        if flag is True:
            if valueIdFinder.getValueId("PROP_BUZZER_ALLOW") in trx.statementsDic and trx.statementsDic[valueIdFinder.getValueId("PROP_BUZZER_ALLOW")].hasResults:
                self.devicePropData.upsAlarmEnable.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_BUZZER_ALLOW")].results[0])

            if valueIdFinder.getValueId("PROP_MODEL_NAME") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_MODEL_NAME")].hasResults:
                self.devicePropData.modelName.value = trx.statementsDic[valueIdFinder.getValueId("PROP_MODEL_NAME")].results[0]

            if valueIdFinder.getValueId("PROP_HARDWARE_VERSION") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_HARDWARE_VERSION")].hasResults:
                self.devicePropData.firmwareVer.value = trx.statementsDic[valueIdFinder.getValueId("PROP_HARDWARE_VERSION")].results[0]

            if valueIdFinder.getValueId("PROP_ACTIVE_POWER") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_ACTIVE_POWER")].hasResults:
                self.devicePropData.activePower.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_ACTIVE_POWER")].results[0])  # already checked

            if valueIdFinder.getValueId("PROP_APPARENT_POWER") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_APPARENT_POWER")].hasResults:
                self.devicePropData.apparentPower.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_APPARENT_POWER")].results[0])  # already checked

            if valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH")].hasResults:
                self.devicePropData.upperLimitProperty.value = trx.statementsDic[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_HIGH")].results[0]

            if valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW") in trx.statementsDic and trx.statementsDic[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW")].hasResults:
                self.devicePropData.lowerLimitProperty.value = trx.statementsDic[valueIdFinder.getValueId("PROP_TRANSFER_VOLT_LOW")].results[0]

            if valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH")].hasResults:
                self.devicePropData.upperLimitList.value = trx.statementsDic[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_HIGH")].results

            if valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW")].hasResults:
                self.devicePropData.lowerLimitList.value = trx.statementsDic[valueIdFinder.getValueId("PROP_LIST_TRANSFER_VOLT_LOW")].results

            if valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY")].hasResults:
                self.devicePropData.sensitivity.value = trx.statementsDic[valueIdFinder.getValueId("PROP_VOLT_SENSITIVITY")].results[0]

            if valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].hasResults:
                self.devicePropData.cumulativeEnergyConsumption.value = trx.statementsDic[valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].results[0]

            if valueIdFinder.getValueId("PROP_RATING_VOLT") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_RATING_VOLT")].hasResults:
                self.devicePropData.voltRating.value = trx.statementsDic[valueIdFinder.getValueId("PROP_RATING_VOLT")].results[0]

            if valueIdFinder.getValueId("PROP_SERIAL_NUMBER") in trx.statementsDic and trx.statementsDic[valueIdFinder.getValueId("PROP_SERIAL_NUMBER")].hasResults:
                self.devicePropData.serialNumber.value = trx.statementsDic[valueIdFinder.getValueId("PROP_SERIAL_NUMBER")].results[0]

            if valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD") in trx.statementsDic and trx.statementsDic[
                valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD")].hasResults:
                self.devicePropData.batteryRuntime.value = int(trx.statementsDic[valueIdFinder.getValueId("PROP_BATTERY_RUNTIME_THRESDHOLD")].results[0])

            if valueIdFinder.getValueId("PROP_UPS_EVENT_CODE") in trx.statementsDic and trx.statementsDic[valueIdFinder.getValueId("PROP_UPS_EVENT_CODE")].hasResults:
                self.devicePropData.upsEventCode.value = trx.statementsDic[valueIdFinder.getValueId("PROP_UPS_EVENT_CODE")].results

            self.deviceId = trx.deviceId
            self.propertySignal.emit(self)

        Logger.LogIns().logger.info("***[PropFetcher] serialNumber checked: {0} ***".format(str(self.devicePropData.serialNumber.value)))

    def fetchP44EnergyConsumption(self, helper, deviceId):

            trx = Transaction.Transaction()
            trx.setDeviceId(deviceId)
            valueIdFinder = ValueId.ValueIdFinder()
            cumulativeEnergyConsumptionStatement = Statement.Statement(
                valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION"))

            # if self.devicePropData.cumulativeEnergyConsumption.isChanged():
            trx.add(cumulativeEnergyConsumptionStatement)

            flag = helper.submit(trx)  # Get transaction from device
            if flag is True:
                if valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION") in trx.statementsDic and \
                        trx.statementsDic[
                            valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].hasResults:
                    self.devicePropData.cumulativeEnergyConsumption.value = \
                    trx.statementsDic[valueIdFinder.getValueId("PROP_CUMULATIVE_ENERGY_CONSUMPTION")].results[0]
                else:
                    # self.devicePropData.cumulativeEnergyConsumption = float(0)
                    self.devicePropData.cumulativeEnergyConsumption.clearAvailable()
                    self.devicePropData.cumulativeEnergyConsumption.clearConfigurable()

    def printLog(self, stat, ValueId):

        f1 = True
        if stat is None:
            Logger.LogIns().logger.info("***[PropFetcher] stat: {0} is None ***".format(ValueId))
            f1 = False

        f2 = True
        if not stat.hasResults:
            Logger.LogIns().logger.info("***[PropFetcher] stat: {0} not hasResults ***".format(ValueId))
            f2 = False

        if f1 and f2:
            Logger.LogIns().logger.info("***[PropFetcher] stat: {0} value = {1} ***".format(ValueId, stat.results[0]))
