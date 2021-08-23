import sys
import traceback

from PyQt5.QtCore import pyqtSignal, QObject

from major import Command
from Utility import Logger

class SelfTestHandler(QObject):
    aaa = pyqtSignal(object)
    def __init__(self, selfTestPage, client, device):
        super(SelfTestHandler, self).__init__()
        self.selfTestPage = selfTestPage
        self.client = client
        self.device = device
        self.selfTestFlag = False  # 確認selfTest由view進行觸發
        self.selfTestCount = 0  # 計算機器回傳值次數

        self.client.updateConfigSettingSignal.connect(self.restoreSelfTestSlot)
        self.selfTestPage.doSelfTestSignal.connect(self.doSelfTestSlot)
        self.client.deviceStatusUpdateSignal.connect(self.isSelfTestProcessingSlot)

    def doSelfTestSlot(self):
        self.selfTestFlag = True
        # configData = self.device.deviceConfigure.configParam()
        # configData.CMD_BATTERY_TEST = 1

        if self.device.deviceId != -1:  # 偵測到機器
            self.client.queryRequest(Command.TARGET_SET_SELF_TEST, "")

        else:  # 未偵測到機器
            Logger.LogIns().logger.info("do self test failed")
            self.selfTestPage.selfTestBtn.setEnabled(False)
    #
    def isSelfTestProcessingSlot(self, deviceStatus):

        if deviceStatus.UtilityPowerFailure:
            self.selfTestPage.selfTestBtn.setEnabled(False)
        else:

            try:
                if self.device.deviceId != -1:  # 偵測到機器
                    if self.selfTestFlag:  # 確認selfTest由view進行觸發
                        self.selfTestCount += 1
                        # 為避免下self-test指令與機器回傳BatteryTesting結果之時間差造成判斷錯誤, 程式會忽略第一次傳回之BatteryTesting
                        if self.selfTestCount > 2 and deviceStatus.BatteryTesting is False:
                            self.selfTestFlag = False
                            self.selfTestCount = 0
                            ispassed = deviceStatus.HardwareFault is False  # ispassed表示self-test通過與否, t為通過
                            self.client.queryRequest(Command.TARGET_CONFIG)
                            self.updateSelfTestResult()
                            Logger.LogIns().logger.info("Self test finished")
                    else:  # 若偵測到機器, 且非selfTest進行中
                        if deviceStatus.BatteryTesting:  # 由機器面板觸發
                            self.selfTestPage.selfTestBtn.setEnabled(False)
                            self.selfTestPage.loadingIcon.show()
                            self.selfTestFlag = True
                        else:
                            self.selfTestPage.selfTestBtn.setEnabled(True)  # 機器接回來時
                else:  # 未偵測到機器
                    self.selfTestPage.selfTestBtn.setEnabled(False)
                    self.selfTestPage.loadingIcon.hide()
            except Exception:
                Logger.LogIns().logger.error(traceback.format_exc())

    def updateSelfTestResult(self):
        self.selfTestPage.isSelfTestProcessing(False)

    def restoreSelfTestSlot(self, config):
        self.selfTestPage.restoreSelfTest(config)
