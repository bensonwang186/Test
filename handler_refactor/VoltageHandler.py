import traceback

import sys

from controllers import DeviceConfigure
from controllers import TransactionHelper


class VoltageHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.server.setVoltageSignal.connect(self.setVoltage)

    def setVoltage(self, tupleData):
        configData = self.device.deviceConfigure.configParam()

        if tupleData[1]:
            configData.SET_TRANSFER_VOLT_LOW = 1
        else:
            configData.SET_TRANSFER_VOLT_HIGH = 1

        configData.params.append(tupleData[0])

        if self.device.deviceId != -1:
            flag = self.device.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)

            if flag:
                print("set Voltage success")
            else:
                print("set Voltage fail")

            return flag
