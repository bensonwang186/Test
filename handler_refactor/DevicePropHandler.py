from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from major import Command
from Utility import Logger
from System import systemFunction


class DevicePropHandler(QObject):
    def __init__(self, server, device):
        super(DevicePropHandler, self).__init__()
        self.devicePropData = device.devicePropData
        self.server = server
        self.device = device
        self.initSlot()

    def initSlot(self):
        self.devicePropData.updatePropertySignal.connect(self.propertiesChangedSlot)
        self.devicePropData.disableConfigureSignal.connect(self.disableConfigureSlot)

    @QtCore.pyqtSlot(object)
    def propertiesChangedSlot(self, data):
        self.server.sendDataToClients(Command.TARGET_PROPERTY, data.toJson())
        self.setDevicePropToSilenceMsg(data)

    def disableConfigureSlot(self, data):
        self.masterPage.disableConfigure()

    def setDevicePropToSilenceMsg(self, data):
        # self.devicePushSilenceMsg.powerSupply = data
        # self.devicePushSilenceMsg.voltage = data
        # self.devicePushSilenceMsg.condition = data
        # self.devicePushSilenceMsg.capacity = data
        # self.devicePushSilenceMsg.batteryStatus = data
        # self.devicePushSilenceMsg.runtime = data
        # self.devicePushSilenceMsg.load = data
        self.device.devicePushSilenceMsg.Model = data.modelName.value
        self.device.devicePushSilenceMsg.FV = data.firmwareVer.value
        self.device.devicePushSilenceMsg.LP = data.activePower.value
        self.device.devicePushSilenceMsg.RatPow = data.apparentPower.value
        self.device.devicePushSilenceMsg.SN = data.serialNumber.value

        if systemFunction.stringIsNullorEmpty(data.serialNumber.value) is True:  # SN為空
            self.device.isNoneSN = True
        else:
            self.device.isNoneSN = False

        Logger.LogIns().logger.info("***[d-DevicePropHandler]setDevicePropToSilenceMsg data.serialNumber.value: " + str(data.serialNumber.value) + "***")
        Logger.LogIns().logger.info("***[d-DevicePropHandler]setDevicePropToSilenceMsg devicePushSilenceMsg sn: " + str(self.device.devicePushSilenceMsg.SN) + "***")
        Logger.LogIns().logger.info("***[d-DevicePropHandler]setDevicePropToSilenceMsg isNoneSN: " + str(self.device.isNoneSN) + "***")

        self.device.propertyFetcher.mobileLoginSignal.emit(0)

        # self.devicePushSilenceMsg.countrySelection = data
        # self.devicePushSilenceMsg.energyCost = data
        # self.devicePushSilenceMsg.co2Emitted = data
        # self.devicePushSilenceMsg.unit = data
        # self.devicePushSilenceMsg.statistic = data
        # self.devicePushSilenceMsg.powerProblem = data
