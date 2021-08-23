from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from controllers import TransactionHelper
from major import Command


class DeviceStatusHandler(QObject):
    def __init__(self, server, device):
        super(DeviceStatusHandler, self).__init__()
        self.device = device
        self.helper = TransactionHelper.TransactionHelper()
        self.server = server
        self.initSlot()

    def initSlot(self):
        self.device.deviceStatus.statusSignal.connect(self.deviceStatusUpdate)

    @QtCore.pyqtSlot(object)
    def deviceStatusUpdate(self, deviceStatus):
        # pass
        self.server.sendDataToClients(Command.TARGET_STATUS, deviceStatus.toJson())
        # self.server.sendDataToClients(Command.TARGET_STOP, "{}")
