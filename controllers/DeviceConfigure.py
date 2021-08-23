import json
from PyQt5.QtCore import pyqtSignal, QObject
from System import ValueId
from controllers import TransactionHelper
from model_Json import Transaction, Statement, DataSource2


class DeviceConfigure(QObject):
    settingsSignal = pyqtSignal(object)

    def __init__(self):
        super(DeviceConfigure, self).__init__()
        self.helper = TransactionHelper.TransactionHelper()
        self.everConnected = -1
        self.buzzerAllow = 1
        self.batteryRuntime = -1
        self.transactionData = Transaction.Transaction()

    def setBuzzerAllow(self, flag):
        if flag:
            self.buzzerAllow = 1
        else:
            self.buzzerAllow = 0

    def setBatteryRuntime(self, batteryRuntime):
        self.batteryRuntime = batteryRuntime * 60

    def uncfgBuzzerAllow(self):
        self.buzzerAllow = -1

    def uncfgBatteryRuntime(self):
        self.batteryRuntime = -1

    def uncfgAll(self):
        self.buzzerAllow = -1
        self.batteryRuntime = -1

    def deviceConfigSubmit(self, data, deviceId):

        trx = Transaction.Transaction()
        trx.setDeviceId(deviceId)
        valueIdFinder = ValueId.ValueIdFinder()

        if data.buzzerAllow is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("SET_BUZZER_ALLOW"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.CMD_CANCEL_SCHEDULE is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("CMD_CANCEL_SCHEDULE"))
            trx.add(stat)
        elif data.CMD_SHUTDOWN is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("CMD_SHUTDOWN"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.CMD_SLEEP is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("CMD_SLEEP"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.CMD_SHUTDOWN_RESTORE is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("CMD_SHUTDOWN_RESTORE"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.SET_TRANSFER_VOLT_HIGH is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("SET_TRANSFER_VOLT_HIGH"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.SET_TRANSFER_VOLT_LOW is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("SET_TRANSFER_VOLT_LOW"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.SET_VOLT_SENSITIVITY is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("SET_VOLT_SENSITIVITY"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.SET_BATTERY_RUNTIME is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("SET_BATTERY_RUNTIME_THRESDHOLD"))
            for param in data.params:
                stat.params.append(param)
            trx.add(stat)
        elif data.CMD_BATTERY_TEST is not -1:
            stat = Statement.Statement(valueIdFinder.getValueId("CMD_BATTERY_TEST"))
            trx.add(stat)

        # check has any statement existence
        if (not trx.statements) is not True:
            b = self.helper.submit(trx)
            self.uncfgAll()
            if not b:
                return False
            else:
                self.transactionData = trx

        return True

    def fetchAllConfig(self):
        """read all user's device settings from DB"""

        config = DataSource2.DataSource2().readActiveConfig()
        self.settingsSignal.emit(config)

    class configParam:

        def __init__(self):
            self.buzzerAllow = -1
            self.CMD_SHUTDOWN = -1
            self.CMD_SLEEP = -1
            self.CMD_SHUTDOWN_RESTORE = -1
            self.CMD_CANCEL_SCHEDULE = -1
            self.SET_TRANSFER_VOLT_HIGH = -1
            self.SET_TRANSFER_VOLT_LOW = -1
            self.SET_VOLT_SENSITIVITY = -1
            self.SET_BATTERY_RUNTIME = -1
            self.CMD_BATTERY_TEST = -1
            self.params = []

        def toJson(self):
            return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
                              separators=(',', ':'))
