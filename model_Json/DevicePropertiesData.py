import json
import sys
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject

from System import systemDefine as sysDef, systemFunction


class DevicePropertiesData(QObject):
    updatePropertySignal = pyqtSignal(object)
    disableConfigureSignal = pyqtSignal(object)

    def __init__(self, jsonString = None):
        super(DevicePropertiesData, self).__init__()

        self.upsAlarmEnable = BoolValue(available=True, configurable=True)
        self.modelName = StringValue(available=True, configurable=False)
        self.serialNumber = StringValue(available=True, configurable=False)
        self.firmwareVer = StringValue(available=True, configurable=False)
        self.powerRating = StringValue(available=True, configurable=True)
        self.voltRating = IntValue(available=True, configurable=True)
        self.modelName.value = sysDef.unknownStr
        self.serialNumber.value = sysDef.unknownStr
        self.firmwareVer.value = sysDef.unknownStr
        self.powerRating.value = sysDef.unknownStr

        self.upperLimitProperty = IntValue(available=True, configurable=True)
        self.lowerLimitProperty = IntValue(available=True, configurable=True)
        self.upperLimitList = IntListValue(available=True, configurable=False)
        self.lowerLimitList = IntListValue(available=True, configurable=False)

        self.batteryTesting = BoolValue(available=True, configurable=True)
        self.hardwareFault = BoolValue(available=True, configurable=True)

        self.sensitivity = IntValue(available=True, configurable=True)

        # battery runtime info
        self.batteryRuntimeRange = IntListValue(available=True, configurable=False)
        self.batteryRuntime = IntValue(available=True, configurable=True)

        self.activePower = IntValue(available=True, configurable=False)
        self.apparentPower = IntValue(available=True, configurable=False)
        self.cumulativeEnergyConsumption = FloatValue(available=True, configurable=False)
        self.configChangeSyncId = IntValue()
        self.configChangeId = IntValue()

        self.batteryLifeSpanMonth = IntValue(available=False, configurable=False)
        self.batteryExpired = BoolValue(available=False, configurable=False)

        self.upsEventCode = StringValue(available=True, configurable=False)

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def disableConfigureSlot(self):
        self.disableConfigureSignal.emit(self)

    @QtCore.pyqtSlot(object)
    def updatePropertiesSignal(self):
        self.updatePropertySignal.emit(self)

    def valueHandler(self, x):
        if isinstance(x, (IntValue, StringValue, BoolValue, Value)):
            try:
                xd = x.value
                return xd
            except Exception:
                traceback.print_exc(file=sys.stdout)
        raise TypeError("Unknown type")

    def toJson(self):
        return json.dumps(self.__dict__, default=self.valueHandler)

class Value:
    def __init__(self, *args, **kwargs):  # Always use self for the first argument to instance methods.
        # args -- tuple of anonymous arguments
        # kwargs -- dictionary of named arguments

        if len(kwargs) == 0:
            self.available = True
            self.configurable = False
            self.instant = False
            self.changed = False
            self.valueLegal = True
            # self._lock = threading.Lock()
        else:
            self.available = kwargs["available"]
            self.configurable = kwargs["configurable"]
            self.changed = False
            self.valueLegal = True
            # self._lock = threading.Lock()

    @classmethod  # overloading constructor
    def Value(cls, available, configurable):  # Always use cls for the first argument to class methods
        cls.available = available
        cls.configurable = configurable
        cls.changed = False
        cls.valueLegal = True
        # cls.lock = threading.Lock()

    def isAvailable(self):
        return self.available

    def isConfigurable(self):
        return self.configurable

    def isInstant(self):
        return self.instant

    def isChanged(self):
        return self.changed

    def isValueLegal(self):
        return self.valueLegal

    def clearAvailable(self):
        self.available = False

    def setAvailable(self):
        self.available = True

    def clearConfigurable(self):
        self.configurable = False

    def setConfigurable(self):
        self.configurable = True

    def clearChanged(self):
        self.changed = False

    def setChanged(self):
        self.changed = True

    def setInstant(self, boolValue):
        self.instant = boolValue

    def applyProperty(self, n):
        pass

    def applyConfigError(self):
        self.clearConfigurable()


class IntValue(Value):
    def __init__(self, *args, **kwargs):
        self.value = -1
        # self._lock = threading.Lock()

        if len(kwargs) > 0:
            super().Value(kwargs["available"], kwargs["configurable"])  # super()可用於呼叫父類別定義method

    def value(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def applyConfigError(self, value):
        if systemFunction.intTryParse(value):
            self.setValue(int(value))

    def store(self, node, doc):
        pass

    def restore(self, root):
        pass


class BoolValue(Value):  # 繼承Value
    def __init__(self, *args, **kwargs):
        self.value = False
        # self._lock = threading.Lock()

        if len(kwargs) > 0:
            super().Value(kwargs["available"], kwargs["configurable"])  # super()可用於呼叫父類別定義method

    def value(self):
        return self.value

    def setValue(self, boolValue):
        self.value = boolValue

    def applyProperty(self, n):
        if systemFunction.intTryParse(n):
            boolValue = int(n) != 0
            self.setValue(boolValue)

    def applyConfigError(self):
        self.setValue(False)
        self.clearConfigurable()

    def store(self, node, doc):
        pass

    def restore(self, root):
        pass

        # @property
        # def lock(self):
        #     return self._lock


class StringValue(Value):
    def __init__(self, *args, **kwargs):
        self.value = ""
        self.isValueLegal = True
        # self._lock = threading.Lock()

        if len(kwargs) > 0:
            super().Value(kwargs["available"], kwargs["configurable"])  # super()可用於呼叫父類別定義method

    def value(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def store(self, node, doc):
        pass

    def restore(self, root):
        pass


class IntListValue(Value):
    def __init__(self, *args, **kwargs):
        self.value = list()
        self.isValueLegal = True
        # self._lock = threading.Lock()

        if len(kwargs) > 0:
            super().Value(kwargs["available"], kwargs["configurable"])  # super()可用於呼叫父類別定義method

    def value(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def store(self, node, doc):
        pass

    def restore(self, root):
        pass


class FloatValue(Value):
    def __init__(self, *args, **kwargs):
        self.value = float(0)
        # self._lock = threading.Lock()

        if len(kwargs) > 0:
            super().Value(kwargs["available"], kwargs["configurable"])  # super()可用於呼叫父類別定義method

    def value(self):
        return self.value

    def setValue(self, value):
        self.value = value