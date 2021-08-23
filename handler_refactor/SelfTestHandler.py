from System import ValueId
from System.systemDefine import TestResult, TestResultType, TestType

from Utility import Logger

class SelfTestHandler:
    def __init__(self, server, device):
        self.EventID = device.cloudEventId
        self.server = server
        self.device = device
        self.selfTestFlag = False  # 確認selfTest由view進行觸發
        self.selfTestCount = 0  # 計算機器回傳值次數

        # self.device.dataSource.updateSelfTestSignal.connect(self.restoreSelfTestSlot)
        self.server.doSelfTestSignal.connect(self.doSelfTestSlot)

    def doSelfTestSlot(self):
        configData = self.device.deviceConfigure.configParam()
        configData.CMD_BATTERY_TEST = 1

        if self.device.deviceId != -1:  # 偵測到機器
            flag = self.device.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)
            valueIdFinder = ValueId.ValueIdFinder()
            if flag:  # 下cmd至機器成功
                Logger.LogIns().logger.info("do self test start")
                trx = self.device.deviceConfigure.transactionData
                if trx.statementsDic[valueIdFinder.getValueId("CMD_BATTERY_TEST")].errCode == 0:  # 機器回傳cmd執行成功
                    self.selfTestFlag = True
                    # 於此無法知道SelfTest執行結果, 只能知道有無執行

                else:  # 機器回傳cmd執行失敗
                    # 目前只有log起來，之後要考慮將結果顯示在UI
                    Logger.LogIns().logger.info("do self test failed")
                    self.server.eventOccurSignal.emit(self.EventID.ID_BATTERY_TEST_FAIL)
            else:  # 下cmd至機器失敗
                # 目前只有log起來，之後要考慮將結果顯示在UI
                Logger.LogIns().logger.info("do self test failed")
                self.server.eventOccurSignal.emit(self.EventID.ID_BATTERY_TEST_FAIL)

        else:  # 未偵測到機器
            Logger.LogIns().logger.info("do self test failed")

