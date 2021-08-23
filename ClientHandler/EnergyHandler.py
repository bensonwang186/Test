import json
import sys
import traceback

from PyQt5.QtCore import QTimer

from System import systemFunction
from major import Command
from Utility import Logger

class EnergyHandler(object):
    def __init__(self, settingPage, reportingPage, client):
        self.settingPage = settingPage
        self.reportingPage = reportingPage
        self.client = client
        self.hourTimer = QTimer()
        self._cumEnergyConsumptionBase = -1
        self._cumEnergyConsumptionUpdate = -1
        self.energySettings = None
        self.energyCost = None
        self.energySettingsTemp = None
        self.energyCostTemp = None
        self.energyConsumptionFlag = None

        # device._propertyFetcher.propertySignal.connect(self.energyConsumptionScheduler)
        # device._devicePropData.updatePropertySignal.connect(self.updateEnergyConsumptionFromDeviceProp)

        self.client.energySettingsUpdateSignal.connect(self.restoreEnergySettingSlot)

        self.settingPage.setEnergySettingSignal.connect(self.updateEnergySettingSlot)
        self.client.setEnergySettingResultSignal.connect(self.updateEnergySettingResultSlot)
        self.settingPage.refreshSignal.connect(self.restoreEnergySettingCacheSlot)
        self.reportingPage.refreshSignal.connect(self.restoreEnergyReporting)
        self.client.energyReportingSignal.connect(self.reportingUpdateSlot)
        self.reportingPage.energyReportingSignal.connect(self.reportingQuerySlot)

    def updateEnergySettingSlot(self, tupleData):
        try:
            ar = [tupleData[0], tupleData[1]]
            self.energySettingsTemp = tupleData[0]
            self.energyCostTemp = tupleData[1]

            jsonData = json.dumps(ar, ensure_ascii=False, default=systemFunction.jsonSerialize)
            print(jsonData)
            print(tupleData)
            self.client.queryRequest(Command.TARGET_SET_ENERGY_SETTINGS, jsonData)
            # result = self.device.dataSource.updateEnergySetting(tupleData)  # db寫入設定
            # self.settingPage.applyResult(result)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def updateEnergySettingResultSlot(self, result):
        if result:
            self.energySettings = self.energySettingsTemp
            self.energyCost = self.energyCostTemp
        self.settingPage.applyResult(result)

    def restoreEnergySettingCacheSlot(self):
        if self.client.isConnected:
            self.restoreEnergySettingSlot((self.energySettings, self.energyCost))
        else:
            self.settingPage.disabledPage(True)

    def restoreEnergySettingSlot(self, settings):
        try:
            self.settingPage.disabledPage(False)
            if settings[0] and settings[1] and len(settings[1]) > 0:
                self.energySettings = settings[0]
                self.energyCost = settings[1]
                self.settingPage.restoreSetting(settings)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def reportingUpdateSlot(self, tupleData):
        self.reportingPage.updateEnergyStatistic(tupleData)

    def reportingQuerySlot(self, tupleData):
        startDate = tupleData[0]
        endDate = tupleData[1]

        now = systemFunction.getDatetimeNonw()
        data = dict()
        data["startDate"] = startDate
        data["endDate"] = endDate
        try:
            jsonData = json.dumps(data, default=systemFunction.datetimeHandler)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
        Logger.LogIns().logger.error("EnergyHandler reportingQuerySlot: " + str(jsonData))
        self.client.queryRequest(Command.TARGET_ENERGY_REPORT, jsonData)

    def restoreEnergyReporting(self):
        now = systemFunction.getDatetimeNonw()
        startDate = now
        endDate = now
        data = dict()
        data["startDate"] = startDate
        data["endDate"] = endDate
        try:
            jsonData = json.dumps(data, default=systemFunction.datetimeHandler)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
        Logger.LogIns().logger.error("EnergyHandler restore energy reporting: "+str(jsonData))
        self.client.queryRequest(Command.TARGET_ENERGY_REPORT, jsonData)
        # indexTuple = self.device.dataSource.energyReportQuery(startDate, endDate)
        # if indexTuple:
        #     self.reportingPage.updateEnergyStatistic(indexTuple)
