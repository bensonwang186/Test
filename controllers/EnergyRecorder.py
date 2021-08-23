import datetime
import functools
import sys
import traceback

from PyQt5.QtCore import QTimer

from System import systemDefine, systemFunction
from Utility import Logger

class EnergyRecorder:
    def __init__(self, device, helper):
        self.device = device
        self.cumEnergyConsumptionBase = None
        self.energyConsumptionFlag = False
        self.hourTimer = None
        self._cumEnergyConsumptionUpdate = None
        self.transactionHelper = helper

    def updateEnergyConsumptionFromDeviceProp(self, dic):
        if dic["Report"] is not None and systemFunction.floatTryParse(dic["Report"]):
            self._cumEnergyConsumptionUpdate = round(float(dic["Report"]), 0)  # 取整數四捨五入

    def energyConsumptionScheduler(self):
        now = datetime.datetime.now()
        # nextClosestTime = now.replace(hour=now.hour, minute=(now.minute + 1), second=00, microsecond=00)  # 測試用

        tempTime = now + datetime.timedelta(hours=1)
        nextClosestTime = tempTime.replace(minute=00, second=00, microsecond=00)
        initSecs = int((nextClosestTime - now).total_seconds())  # 啟動排程時間

        try:
            if self.device.devicePropData.cumulativeEnergyConsumption.available:  # 機器支援PROP_CUMULATIVE_ENERGY_CONSUMPTION(331), 由prop.差值計算
                self.energyConsumptionFlag = True
                self._cumEnergyConsumptionBase = self.device.devicePropData.cumulativeEnergyConsumption.value
            else:  # 若不支援由PPPE進行計算
                self.energyConsumptionFlag = False

            self.hourTimer = QTimer()
            self.hourTimer.setSingleShot(True)
            self.hourTimer.timeout.connect(functools.partial(self.energyConsumptionTimer, initSecs))
            self.hourTimer.start(initSecs * 1000)  # unit: 毫秒
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def energyConsumptionTimer(self, initSecs):
        try:
            if self.energyConsumptionFlag:
                self.addEnergyConsumptionByDevice(initSecs)
            else:
                self.addEnergyConsumption(initSecs)

            self.hourTimer = QTimer()
            self.hourTimer.setSingleShot(False)

            if self.energyConsumptionFlag:
                self.hourTimer.timeout.connect(functools.partial(self.addEnergyConsumptionByDevice, None))
            else:
                self.hourTimer.timeout.connect(functools.partial(self.addEnergyConsumption, None))

            # self.hourTimer.start(60000)  # 1min, 測試用
            self.hourTimer.start(3600000)  # 1hr = 3600000毫秒

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def stopEnergyConsumptionTimer(self):
        if self.hourTimer is not None:
            self.hourTimer.stop()
            self.hourTimer = None

    def addEnergyConsumptionByDevice(self, initSecs):
        # 機器耗電差值要補0
        # 換機器要進行判斷(device ID, model name)
        # 斷訊進行處理
        # 不足1hr也需計算(如計14min, 則乘14/60)

        self.device.propertyFetcher.fetchP44EnergyConsumption(self.transactionHelper, self.device.deviceId)

        if self.device.devicePropData.cumulativeEnergyConsumption.available:
            self._cumEnergyConsumptionUpdate = float(self.device.devicePropData.cumulativeEnergyConsumption.value)

        # consumption unit is wh, p44 return kwh, so * 1000
        consumption = float(self._cumEnergyConsumptionUpdate - self._cumEnergyConsumptionBase) * 1000
        if consumption < 0:  # 若機器耗電差值< 0, 則視為0
            consumption = 0
        else:
            if initSecs is not None:
                consumption = consumption * ((initSecs / 60) / 60)  # 不足1hr計算(如計14min, 則乘14/60)

        print("Timer start at:" + str(datetime.datetime.now()))
        flag = self.device.dataSource.addEnergyConsumption(consumption)
        if flag:
            print("add Energy Consumption success(from device cmd)")

    def addEnergyConsumption(self, initSecs):
        try:
            print("Energy Consumption Timer start at:" + str(datetime.datetime.now()))

            divide = (60 / systemDefine.DEVICE_MONITOR_INTERVAL) * 60  # Energy Consumption每3秒計1次, 1分鐘計20次, 1小時計1200次, divide = 1200
            consumption = self.device.cumEnergyConsumptionMonitor / divide  # unit: Wh

            flag = self.device.dataSource.addEnergyConsumption(consumption)
            if flag:
                self.device.cumEnergyConsumptionMonitor = 0
                print("add EnergyConsumption success")

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
