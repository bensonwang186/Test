import json


class SilenceMessage:

    def __init__(self, jsonString=None):
        self._InSta = None
        self._InVolt = None
        self._InFreq = None
        self._OutSta = None
        self._OutVolt = None
        self._OutFreq = None
        self._OutCur = None
        self._BatSta = None
        self._BatCap = None
        self._BatRun = None
        self._BatVolt = None
        self._BatWar = None
        self._BatTRes = None
        self._BatTDate = None
        self._BatTFrom = None
        self._Brd = None
        self._BrdFrom = None
        self._Brdm = None
        self._SysSta = None
        self._SysTemp = None
        self._FaultCode = None
        self._EventCode = None
        self._EventCodeRestore = None
        self._EventCodeNew = None
        self._EnvTemp = None
        self._EnvHumi = None
        self._SN = None
        self._LP = None
        self._Model = None
        self._FV = None
        self._RatPow = None
        self._VoltRat = None
        self._WorFreq = None
        self._upsState = None
        self._Type = 0  # 0/1/2, (UPS/Phone/RMC)
        self._Event = self.Event()
        self._NclOut = None
        self._Out = None
        self._PowSour = None
        self._Dev = 0  # 0/1/2, (UPS/ATS/PDU)
        self._Load = None
        self._BatVoltRat = None
        self._lFV = None
        self._uFV = None

        self._countrySelection = None
        self._energyCost = None
        self._co2Emitted = None
        self._unit = None
        self._statistic = None
        self._powerProblem = None
        self._upsName = None
        self._upsState = None
        # self._uSN = None
        self._tstamp = None

        self._Act = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

        # The price of JSON’s interoperability is that we cannot store arbitrary Python objects.
        # Custom class must be converted, or converting object to JSON will fail.
        # __dict__ is a simple catch-all for user-defined objects, but we can also add support for other objects.

    def toJson(self):
        return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
                          separators=(',', ':'))

    @property
    def InSta(self):
        return self._InSta

    @InSta.setter
    def InSta(self, value):
        self._InSta = value

    @property
    def InVolt(self):
        return self._InVolt

    @InVolt.setter
    def InVolt(self, value):
        self._InVolt = value

    @property
    def InFreq(self):
        return self._InFreq

    @InFreq.setter
    def InFreq(self, value):
        self._InFreq = value

    @property
    def OutFreq(self):
        return self._OutFreq

    @OutFreq.setter
    def OutFreq(self, value):
        self._OutFreq = value

    @property
    def OutCur(self):
        return self._OutCur

    @OutCur.setter
    def OutCur(self, value):
        self._OutCur = value

    @property
    def BatVolt(self):
        return self._BatVolt

    @BatVolt.setter
    def BatVolt(self, value):
        self._BatVolt = value

    @property
    def BatWar(self):
        return self._BatWar

    @BatWar.setter
    def BatWar(self, value):
        self._BatWar = value

    @property
    def Brd(self):
        return self._Brd

    @Brd.setter
    def Brd(self, value):
        self._Brd = value

    @property
    def BrdFrom(self):
        return self._BrdFrom

    @BrdFrom.setter
    def BrdFrom(self, value):
        self._BrdFrom = value

    @property
    def Brdm(self):
        return self._Brdm

    @Brdm.setter
    def Brdm(self, value):
        self._Brdm = value

    @property
    def SysTemp(self):
        return self._SysTemp

    @SysTemp.setter
    def SysTemp(self, value):
        self._SysTemp = value

    @property
    def FaultCode(self):
        return self._FaultCode

    @FaultCode.setter
    def FaultCode(self, value):
        self._FaultCode = value

    @property
    def EnvTemp(self):
        return self._EnvTemp

    @EnvTemp.setter
    def EnvTemp(self, value):
        self._EnvTemp = value

    @property
    def EnvHumi(self):
        return self._EnvHumi

    @EnvHumi.setter
    def EnvHumi(self, value):
        self._EnvHumi = value

    @property
    def LP(self):
        return self._LP

    @LP.setter
    def LP(self, value):
        self._LP = value

    @property
    def VoltRat(self):
        return self._VoltRat

    @VoltRat.setter
    def VoltRat(self, value):
        self._VoltRat = value

    @property
    def WorFreq(self):
        return self._WorFreq

    @WorFreq.setter
    def WorFreq(self, value):
        self._WorFreq = value

    @property
    def BatVoltRat(self):
        return self._BatVoltRat

    @BatVoltRat.setter
    def BatVoltRat(self, value):
        self._BatVoltRat = value

    @property
    def lFV(self):
        return self._lFV

    @lFV.setter
    def lFV(self, value):
        self._lFV = value

    @property
    def uFV(self):
        return self._uFV

    @uFV.setter
    def uFV(self, value):
        self._uFV = value
    @property
    def SysSta(self):
        return self._SysSta

    @SysSta.setter
    def SysSta(self, value):
        self._SysSta = value

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value):
        self._Type = value

    @property
    def Dev(self):
        return self._Dev

    @Dev.setter
    def Dev(self, value):
        self._Dev = value

    @property
    def Event(self):
        return self._Event

    @Event.setter
    def Event(self, value):
        self._Event = value

    @property
    def PowSour(self):
        return self._PowSour

    @PowSour.setter
    def PowSour(self, value):
        self._PowSour = value

    @property
    def OutVolt(self):
        return self._OutVolt

    @OutVolt.setter
    def OutVolt(self, value):
        self._OutVolt = value

    @property
    def OutSta(self):
        return self._OutSta

    @OutSta.setter
    def OutSta(self, value):
        self._OutSta = value

    @property
    def BatCap(self):
        return self._BatCap

    @BatCap.setter
    def BatCap(self, value):
        self._BatCap = value

    @property
    def BatSta(self):
        return self._BatSta

    @BatSta.setter
    def BatSta(self, value):
        self._BatSta = value

    @property
    def BatRun(self):
        return self._BatRun

    @BatRun.setter
    def BatRun(self, value):
        self._BatRun = value

    @property
    def Load(self):
        return self._Load

    @Load.setter
    def Load(self, value):
        self._Load = value

    @property
    def Model(self):
        return self._Model

    @Model.setter
    def Model(self, value):
        self._Model = value

    @property
    def FV(self):
        return self._FV

    @FV.setter
    def FV(self, value):
        self._FV = value

    @property
    def RatPow(self):
        return self._RatPow

    @RatPow.setter
    def RatPow(self, value):
        self._RatPow = value

    @property
    def Out(self):
        return self._Out

    @Out.setter
    def Out(self, value):
        self._Out = value

    @property
    def NclOut(self):
        return self._NclOut

    @NclOut.setter
    def NclOut(self, value):
        self._NclOut = value

    @property
    def SN(self):
        return self._SN

    @SN.setter
    def SN(self, value):
        self._SN = value

    @property
    def countrySelection(self):
        return self._countrySelection

    @countrySelection.setter
    def countrySelection(self, value):
        self._countrySelection = value

    @property
    def energyCost(self):
        return self._energyCost

    @energyCost.setter
    def energyCost(self, value):
        self._energyCost = value

    @property
    def co2Emitted(self):
        return self._co2Emitted

    @co2Emitted.setter
    def co2Emitted(self, value):
        self._co2Emitted = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def statistic(self):
        return self._statistic

    @statistic.setter
    def statistic(self, value):
        self._statistic = value

    @property
    def powerProblem(self):
        return self._powerProblem

    @powerProblem.setter
    def powerProblem(self, value):
        self._powerProblem = value

    @property
    def upsName(self):
        return self._upsName

    @upsName.setter
    def upsName(self, value):
        self._upsName = value

    @property
    def upsState(self):
        return self._upsState

    @upsState.setter
    def upsState(self, value):
        self._upsState = value

    @property
    def tstamp(self):
        return self._tstamp

    @tstamp.setter
    def tstamp(self, value):
        self._tstamp = value

    @property
    def InSta(self):
        return self._InSta

    @InSta.setter
    def InSta(self, value):
        self._InSta = value

    class Event:

        def __init__(self):
            self.I = None  # Input Line Status
            self.O = None  # Output Line Status 
            self.U = None  # UPS Status
            self.B = None  # Battery Status
            self.D = None  # Diagnostics
            self.C = None  # UPS Communication 

    @property
    def BatTRes(self):
        return self._BatTRes

    @BatTRes.setter
    def BatTRes(self, value):
        self._BatTRes = value

    @property
    def BatTDate(self):
        return self._BatTDate

    @BatTDate.setter
    def BatTDate(self, value):
        self._BatTDate = value

    @property
    def BatTFrom(self):
        return self._BatTFrom

    @BatTFrom.setter
    def BatTFrom(self, value):
        self._BatTFrom = value

    @property
    def EventCode(self):
        return self._EventCode

    @EventCode.setter
    def EventCode(self, value):
        self._EventCode = value

    @property
    def EventCodeRestore(self):
        return self._EventCodeRestore

    @EventCodeRestore.setter
    def EventCodeRestore(self, value):
        self._EventCodeRestore = value

    @property
    def EventCodeNew(self):
        return self._EventCodeNew

    @EventCodeNew.setter
    def EventCodeNew(self, value):
        self._EventCodeNew = value

    @property
    def Act(self):
        return self._Act

    @Act.setter
    def Act(self, value):
        self._Act = value

class AlertMessage:

    def __init__(self):
        self._messageTitle = None
        self._messageBody = None

    @property
    def messageTitle(self):
        return self._messageTitle

    @messageTitle.setter
    def messageTitle(self, value):
        self._messageTitle = value

    @property
    def messageBody(self):
        return self._messageBody

    @messageBody.setter
    def messageBody(self, value):
        self._messageBody = value

class EnergyReportStatistic:

    def __init__(self):
        self._averageConsumption = None
        self._cumulativeConsumption = None
        self._cost = None
        self._co2 = None

    @property
    def averageConsumption(self):
        return self._averageConsumption

    @averageConsumption.setter
    def averageConsumption(self, value):
        self._averageConsumption = value

    @property
    def cumulativeConsumption(self):
        return self._cumulativeConsumption

    @cumulativeConsumption.setter
    def cumulativeConsumption(self, value):
        self._cumulativeConsumption = value

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost = value

    @property
    def co2(self):
        return self._co2

    @co2.setter
    def co2(self, value):
        self._co2 = value

class powerProblemSummary:

    def __init__(self):
        self._powerOutageTimes = None
        self._powerOutageAmount = None
        self._underVoltageTimes = None
        self._underVoltageAmount = None
        self._overVoltageTimes = None
        self._overVoltageAmount = None
        self._boostTimes = None
        self._boostAmount = None
        self._buckTimes = None
        self._buckAmount = None

    @property
    def powerOutageTimes(self):
        return self._powerOutageTimes

    @powerOutageTimes.setter
    def powerOutageTimes(self, value):
        self._powerOutageTimes = value

    @property
    def powerOutageAmount(self):
        return self._powerOutageAmount

    @powerOutageAmount.setter
    def powerOutageAmount(self, value):
        self._powerOutageAmount = value

    @property
    def underVoltageTimes(self):
        return self._underVoltageTimes

    @underVoltageTimes.setter
    def underVoltageTimes(self, value):
        self._underVoltageTimes = value

    @property
    def underVoltageAmount(self):
        return self._underVoltageAmount

    @underVoltageAmount.setter
    def underVoltageAmount(self, value):
        self._underVoltageAmount = value

    @property
    def overVoltageTimes(self):
        return self._overVoltageTimes

    @overVoltageTimes.setter
    def overVoltageTimes(self, value):
        self._overVoltageTimes = value

    @property
    def overVoltageAmount(self):
        return self._overVoltageAmount

    @overVoltageAmount.setter
    def overVoltageAmount(self, value):
        self._overVoltageAmount = value

    @property
    def boostTimes(self):
        return self._boostTimes

    @boostTimes.setter
    def boostTimes(self, value):
        self._boostTimes = value

    @property
    def boostAmount(self):
        return self._boostAmount

    @boostAmount.setter
    def boostAmount(self, value):
        self._boostAmount = value

    @property
    def buckTimes(self):
        return self._buckTimes

    @buckTimes.setter
    def buckTimes(self, value):
        self._buckTimes = value

    @property
    def buckAmount(self):
        return self._buckAmount

    @buckAmount.setter
    def buckAmount(self, value):
        self._buckAmount = value

class BatteryTestResult:

    def __init__(self):
        self._BatTRes = None
        self._BatTDate = None
        self._BatTFrom = None

    @property
    def BatTRes(self):
        return self._BatTRes

    @BatTRes.setter
    def BatTRes(self, value):
        self._BatTRes = value

    @property
    def BatTDate(self):
        return self._BatTDate

    @BatTDate.setter
    def BatTDate(self, value):
        self._BatTDate = value

    @property
    def BatTFrom(self):
        return self._BatTFrom

    @BatTFrom.setter
    def BatTFrom(self, value):
        self._BatTFrom = value
