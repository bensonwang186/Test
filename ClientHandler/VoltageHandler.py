import traceback

import sys

from major import Command

class VoltageHandler(object):
    def __init__(self, voltagePage, client):
        self.voltagePage = voltagePage
        self.client = client
        self.voltagePage.setVoltageSignal.connect(self.setVoltage)

    def setVoltage(self, tupleData):
        self.client.queryRequest(Command.TARGET_SET_TRANSFER_VOLT, tupleData)