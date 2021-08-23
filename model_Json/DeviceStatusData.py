from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
import json

class DeviceStatus(QObject):

    _statusSignal = pyqtSignal(object)

    def __init__(self, jsonString = None):
        super(DeviceStatus, self).__init__()
        #test comment
        self._deviceId = -1
        self._OutputStatus = None  # "_" is weak "internal use" indicator
        self._OutputVolt = None
        self._OutputFreq = None
        self._OutputCurrent = None
        self._InputStatus = None
        self._InputVolt = None
        self._InputFreq = None
        self._BatteryLow = None
        self._BatteryCapacity = None
        self._BatteryStatus = None
        self._RemainingRuntime = None
        self._BatteryVolt = None
        self._LoadWatt = None
        self._UpsTemperature = None
        self._UtilityPowerFailure = False
        self._BatteryTesting = None
        self._HardwareFault = None
        self._OutputOverload = None
        self._PercentLoad = None
        self._SelfTestFWErrFlag = False
        self._UpsEventFlag = 0
        self._UpsEventCode = []
        self._PowerSourceStatus = None
        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def assignDeviceStatus(self, deviceStatus):
        self._OutputStatus = deviceStatus.OutputStatus
        self._OutputVolt = deviceStatus.OutputVolt
        self._OutputFreq = deviceStatus.OutputFreq
        self._OutputCurrent = deviceStatus.OutputCurrent
        self._InputStatus = deviceStatus.InputStatus
        self._InputVolt = deviceStatus.InputVolt
        self._InputFreq = deviceStatus.InputFreq
        self._BatteryCapacity = deviceStatus.BatteryCapacity
        self._BatteryLow = deviceStatus.BatteryLow
        self._BatteryStatus = deviceStatus.BatteryStatus
        self._RemainingRuntime = deviceStatus.RemainingRuntime
        self._BatteryVolt = deviceStatus.BatteryVolt
        self._LoadWatt = deviceStatus.LoadWatt
        self._UtilityPowerFailure = deviceStatus.UtilityPowerFailure
        self._BatteryTesting = deviceStatus.BatteryTesting
        self._HardwareFault = deviceStatus.HardwareFault
        self._deviceId = deviceStatus.deviceId
        self._OutputOverload = deviceStatus.OutputOverload
        self._PercentLoad = deviceStatus.PercentLoad
        self._UpsTemperature = deviceStatus.UpsTemperature
        self._SelfTestFWErrFlag = deviceStatus.SelfTestFWErrFlag
        self._UpsEventFlag = deviceStatus.UpsEventFlag
        self._UpsEventCode = deviceStatus.UpsEventCode
        self._PowerSourceStatus = deviceStatus.PowerSourceStatus
        self._statusSignal.emit(self)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @property
    def deviceId(self):
        return self._deviceId

    @deviceId.setter
    def deviceId(self, value):
        self._deviceId = value
        self._statusSignal.emit(self)

    @property
    def statusSignal(self):
        return self._statusSignal

    @property
    def OutputStatus(self):
        return self._OutputStatus

    @OutputStatus.setter
    def OutputStatus(self, value):
        self._OutputStatus = value

    @OutputStatus.deleter
    def OutputStatus(self):
        del self._OutputStatus

    @property
    def OutputVolt(self):
        return self._OutputVolt

    @OutputVolt.setter
    def OutputVolt(self, value):
        self._OutputVolt = value

    @OutputVolt.deleter
    def OutputVolt(self):
        del self._OutputVolt

    @property
    def OutputFreq(self):
        return self._OutputFreq

    @OutputFreq.setter
    def OutputFreq(self, value):
        self._OutputFreq = value

    @property
    def OutputCurrent(self):
        return self._OutputCurrent

    @OutputCurrent.setter
    def OutputCurrent(self, value):
        self._OutputCurrent = value

    # -----------separator-----------

    @property
    def InputStatus(self):
        return self._InputStatus

    @InputStatus.setter
    def InputStatus(self, value):
        self._InputStatus = value

    @InputStatus.deleter
    def InputStatus(self):
        del self._InputStatus

    # -----------separator-----------

    @property
    def InputVolt(self):
        return self._InputVolt

    @InputVolt.setter
    def InputVolt(self, value):
        self._InputVolt = value

    @InputVolt.deleter
    def InputVolt(self):
        del self._InputVolt

    @property
    def InputFreq(self):
        return self._InputFreq

    @InputFreq.setter
    def InputFreq(self, value):
        self._InputFreq = value

    # -----------separator-----------

    @property
    def BatteryCapacity(self):
        return self._BatteryCapacity

    @BatteryCapacity.setter
    def BatteryCapacity(self, value):
        self._BatteryCapacity = value

    @BatteryCapacity.deleter
    def BatteryCapacity(self):
        del self._BatteryCapacity

    # -----------separator-----------

    @property
    def BatteryLow(self):
        return self._BatteryLow

    @BatteryLow.setter
    def BatteryLow(self, value):
        self._BatteryLow = value

    @BatteryLow.deleter
    def BatteryLow(self):
        del self._BatteryLow

    # -----------separator-----------

    @property
    def RuntimeLow(self):
        return self._RuntimeLow

    @RuntimeLow.setter
    def RuntimeLow(self, value):
        self._RuntimeLow = value

    @RuntimeLow.deleter
    def RuntimeLow(self):
        del self._RuntimeLow

    # -----------separator-----------

    @property
    def BatteryStatus(self):
        return self._BatteryStatus

    @BatteryStatus.setter
    def BatteryStatus(self, value):
        self._BatteryStatus = value

    @BatteryStatus.deleter
    def BatteryStatus(self):
        del self._BatteryStatus

    # -----------separator-----------

    @property
    def RemainingRuntime(self):
        return self._RemainingRuntime

    @RemainingRuntime.setter
    def RemainingRuntime(self, value):
        self._RemainingRuntime = value

    @RemainingRuntime.deleter
    def RemainingRuntime(self):
        del self._RemainingRuntime

    @property
    def BatteryVolt(self):
        return self._BatteryVolt

    @BatteryVolt.setter
    def BatteryVolt(self, value):
        self._BatteryVolt = value

    # -----------separator-----------

    @property
    def LoadWatt(self):
        return self._LoadWatt

    @LoadWatt.setter
    def LoadWatt(self, value):
        self._LoadWatt = value

    @LoadWatt.deleter
    def LoadWatt(self):
        del self._LoadWatt

    @property
    def UtilityPowerFailure(self):
        return self._UtilityPowerFailure

    @UtilityPowerFailure.setter
    def UtilityPowerFailure(self, value):
        self._UtilityPowerFailure = value

    @property
    def BatteryTesting(self):
        return self._BatteryTesting

    @BatteryTesting.setter
    def BatteryTesting(self, value):
        self._BatteryTesting = value

    @property
    def HardwareFault(self):
        return self._HardwareFault

    @HardwareFault.setter
    def HardwareFault(self, value):
        self._HardwareFault = value

    @property
    def OutputOverload(self):
        return self._OutputOverload

    @OutputOverload.setter
    def OutputOverload(self, value):
        self._OutputOverload = value

    @property
    def PercentLoad(self):
        return self._PercentLoad

    @PercentLoad.setter
    def PercentLoad(self, value):
        self._PercentLoad = value

    @property
    def UpsTemperature(self):
        return self._UpsTemperature

    @UpsTemperature.setter
    def UpsTemperature(self, value):
        self._UpsTemperature = value

    @property
    def SelfTestFWErrFlag(self):
        return self._SelfTestFWErrFlag

    @SelfTestFWErrFlag.setter
    def SelfTestFWErrFlag(self, value):
        self._SelfTestFWErrFlag = value

    @property
    def UpsEventFlag(self):
        return self._UpsEventFlag

    @UpsEventFlag.setter
    def UpsEventFlag(self, value):
        self._UpsEventFlag = value

    @property
    def UpsEventCode(self):
        return self._UpsEventCode

    @UpsEventCode.setter
    def UpsEventCode(self, value):
        self._UpsEventCode = value

    @property
    def PowerSourceStatus(self):
        return self._PowerSourceStatus

    @PowerSourceStatus.setter
    def PowerSourceStatus(self, value):
        self._PowerSourceStatus = value

class InputStatus(Enum):
    UtilityFailure = 0
    UtilityLow = 1
    UtilityHigh = 2
    FreqFailure = 3
    UtilityBoost = 4
    UtilityBucket = 5
    Normal = 6

    """
    emq Input  Status
    Power Outage 0
    Under voltage 1
    Over voltage 2
    Frequency failure 3
    Normal 4
    """
    # 取得personal在UI上的input status轉換成emq定義的input status
    def get_publish_input_status(self):
        try:
            input_status = {
                InputStatus.UtilityFailure: 0,
                InputStatus.UtilityLow: 1,
                InputStatus.UtilityHigh: 2,
                InputStatus.FreqFailure: 3,
                InputStatus.Normal: 4
            }[self]
        except Exception:
            input_status = None

        return input_status

class OutputStatus(Enum):
    UtilityPower = 0 # Normal
    BatteryPower = 1 # Normal
    NoOutput = 2
    Overload = 3
    Buck = 4
    Boost = 5
    Bypass = 6
    BypassUPSAbnormal = 7
    BypassOverload = 8
    ManualBypass = 9
    EcoMode = 10

    """
    emq Output Status
    No output 0
    Overload 1
    Voltage buck 2
    Voltage boost 3
    Bypass 4
    Bypass ups abnormal 5
    Bypass overload 6
    Manual bypass 7
    Eco mode 8
    Normal 9
    """
    # 取得personal在UI上的output status轉換成emq定義的output status
    def get_publish_output_status(self):
        try:
            output_status = {
                OutputStatus.NoOutput: 0,
                OutputStatus.Overload: 1,
                OutputStatus.Buck: 2,
                OutputStatus.Boost: 3,
                OutputStatus.Bypass: 4,
                OutputStatus.BypassUPSAbnormal: 5,
                OutputStatus.BypassOverload: 6,
                OutputStatus.ManualBypass: 7,
                OutputStatus.EcoMode: 8,
                OutputStatus.UtilityPower: 9,
                OutputStatus.BatteryPower: 9
            }[self]
        except Exception:
            output_status = None

        return output_status

class BatteryStatus(Enum):
    FullCharge = 0
    Charging = 1
    Discharging = 2

class PowerSourceStatus(Enum):
    UtilityPower = 0
    BatteryPower = 1
    NoOutput = 2

class DeviceState(Enum):
    PROXY_STATE_NORMAL = 0
    PROXY_STATE_NOT_READY = 1
    PROXY_STATE_NOT_AVAILABLE = 2
    PROXY_STATE_FAULT = 3


class THREE_PHASE(Enum):
    STATUS_PHASE1 = 0
    STATUS_PHASE2 = 1
    STATUS_PHASE3 = 2


class POSITIVE_NEGATIVE(Enum):
    STATUS_POSITIVE = 0
    STATUS_NEGATIVE = 1


class Utility(Enum):
    STATUS_NORMAL = 0
    STATUS_POWER_FAILURE = 1
    STATUS_BLACKOUT = 2
    STATUS_OVER_VOLT = 3
    STATUS_UNDER_VOLT = 4
    STATUS_FREQUENCY_FAILURE = 5
    STATUS_WIRING_FAULT = 6
    STATUS_NO_NEUTRAL = 7
    STATUS_GENERATOR_DETECTED = 8


class Output(Enum):
    STATUS_NORMAL = 0
    STATUS_BYPASS = 1
    STATUS_NO_OUTPUT = 2
    STATUS_SHORTED = 3
    STATUS_BYPASS_OVERLOAD = 4  # no used
    STATUS_OVERLOAD = 5
    STATUS_BOOST = 6
    STATUS_BUCK = 7
    STATUS_ECO = 8
    STATUS_MANUAL_BYPASS = 9
    STATUS_EMERGENCY_POWER_OFF = 10
    STATUS_INVERTER_POWER_INSUFFICIENT = 11
    # STATUS_REDUNDANCY_LOST = 12;
    # STATUS_LEAVE_ECO_FREQUENTLY = 13;


class Battery(Enum):
    STATUS_FULLED = 0  # also for 3 - phase
    STATUS_DISCHARGING = 1  # also for 3 - phase
    STATUS_CHARGING = 2
    STATUS_LOW_WARNING = 3
    STATUS_LOW_CRITICAL = 4  # also for 3 - phase
    STATUS_REPLACE_NEED = 5
    STATUS_NOT_PRESENT = 6  # also for 3 - phase
    STATUS_TESTING = 7  # also for 3 - phase
    STATUS_NORMAL = 8  # only for 3 - phase
    STATUS_EXHAUSTED = 9  # only for 3 - phase
    STATUS_REVERSED_CONNECTION = 10  # only for 3 - phase
    STATUS_FLOAT_CHARGING = 11
    STATUS_BOOST_CHARGING = 12
    STATUS_CHARGER_FAILURE = 13
    STATUS_VOLTAGE_OVER = 14
    STATUS_VOLTAGE_UNDER = 15


class System(Enum):
    STATUS_NORMAL = 0
    STATUS_FAULT = 1
    STATUS_FAULT_FAN_ERROR = 2
    STATUS_FAULT_BATTERY_VOLTAGE_OVER = 3
    STATUS_FAULT_BATTERY_VOLTAGE_UNDER = 4
    STATUS_FAULT_RELAY_FAILUR = 5
    STATUS_FAULT_EEPROM_FAILURE = 6
    STATUS_FAULT_CHARGER_FAILURE = 7
    STATUS_OVERHEAT = 8
    STATUS_MODULE_FAILURE = 9
    STATUS_BYPASS_FAULT = 10
    STATUS_BYPASS_FAN_FAULT = 11
    STATUS_REDUNDANCY_LOST = 12
    STATUS_UNABLE_RECOVER = 13


class Bypass(Enum):
    STATUS_NORMAL = 0
    STATUS_POWER_FAILURE = 1
    STATUS_BLACKOUT = 2
    STATUS_OVER_VOLTAGE = 3
    STATUS_UNDER_VOLTAGE = 4
    STATUS_FREQUENCY_FAILURE = 5
    STATUS_WRONG_PHASE_SEQUENCE = 6
    STATUS_OVERLOAD = 7
    STATUS_OVERLOAD_EXPIRED = 8
    # STATUS_TRANSFER_FREQUENTLY = 9


class ErrorCode(Enum):
    DRVERR_SUCCESS = 0
    DRVERR_EXECUTE_FAIL = 1
    DRVERR_DEVICE_WRONG = 2
    DRVERR_CMD_NOT_SUPPORT = 3
    DRVERR_CMD_PARAM_WRONG = 4
    DRVERR_CMD_NOT_ACCPETABLE_NOW = 5
    DRVERR_CMDID_INVALID = 6
    DRVERR_DEVID_INVALID = 7
    DRVERR_OUTLET_CONTROL_FAIL = 8
    DRVERR_OUTLET_NOT_SWITCHABLE = 9
    DRVERR_OUTLET_SCHEDULE_NOT_SUPPORT = 10

class EventCode(Enum):
    NORMAL = 0
    OCCURRED = 1

if __name__ == "__main__":
    d = DeviceStatus()
    d.InputVolt = 120
    ser = d.toJson()
    print(d.toJson())
    d2 = DeviceStatus(ser)
    print(d2.InputVolt)

