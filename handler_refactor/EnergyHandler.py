import sys
import traceback
from major import Command
from PyQt5.QtCore import QTimer

class EnergyHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.hourTimer = QTimer()
        self._cumEnergyConsumptionBase = -1
        self._cumEnergyConsumptionUpdate = -1
        self.energyConsumptionFlag = None

        self.server.setEnergySettingSignal.connect(self.updateEnergySettingSlot)

    def updateEnergySettingSlot(self, tupleData):
        try:
            result = self.device.dataSource.updateEnergySetting(tupleData)  # db寫入設定
            self.server.sendDataToClients(Command.TARGET_SET_ENERGY_SETTINGS_RESULT, result)

        except Exception:
            traceback.print_exc(file=sys.stdout)
