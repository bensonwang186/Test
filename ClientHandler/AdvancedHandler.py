import traceback
from Utility import DataCryptor

import sys
from major import Command
from Utility import Logger
from System import systemFunction

class AdvancedHandler(object):
    def __init__(self, advancedPage, client, appTray):
        self.advancedPage = advancedPage
        self.client = client
        self.tray = appTray

        self.client.updateConfigSettingSignal.connect(self.updateShutdownTypeConfigSlot)
        self.client.mobileAppLoginSignal.connect(self.setMobileAppLoginStatusSlot)
        self.client.updateUPSNameSignal.connect(self.updateUPSNameStatusSlot)
        self.client.cloud_data_display_signal.connect(self.cloud_data_display_slot)
        self.client.cloud_verify_result_signal.connect(self.cloud_verify_result_slot)

        self.advancedPage.setShutdownTypeSignal.connect(self.setShutdownTypeConfigSlot)
        self.advancedPage.setSensitivitySignal.connect(self.setSensitivity)
        self.advancedPage.viewSetMobileSolutionSignal.connect(self.setMobileSolutionEnableSlot)
        self.advancedPage.viewSetMobileLoginSignal.connect(self.setMobileLoginSlot)
        self.advancedPage.viewUpdateUPSNameSignal.connect(self.updateUPSName)
        self.advancedPage.get_cloud_data_signal.connect(self.get_cloud_data_slot)
        self.advancedPage.cloud_verify_signal.connect(self.cloud_verify_slot)

    def updateShutdownTypeConfigSlot(self, config):
        self.advancedPage.restoreConfigSetting(config)
        self.tray.shutdownType = int(config.shutDownType)

    def setShutdownTypeConfigSlot(self, param):
        self.tray.shutdownType = param
        try:
            self.client.queryRequest(Command.TARGET_SET_SHUTDOWN_TYPE, param)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def setMobileSolutionEnableSlot(self, param):
        try:
            self.client.queryRequest(Command.TARGET_SET_MOBILE_SOLUTION, param)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def setMobileLoginSlot(self, cloud_data):
        try:
            print(cloud_data)
            if systemFunction.stringIsNullorEmpty(cloud_data.password) is False:
                cryptor = DataCryptor.Cryptor()
                cloud_data.password = cryptor.enc(cloud_data.password)

            self.client.queryRequest(Command.TARGET_SET_MOBILE_LOGIN, cloud_data.to_json())
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def setSensitivity(self, param):
        self.client.queryRequest(Command.TARGET_SET_SENSITIVITY, param)

    def setMobileAppLoginStatusSlot(self, loginResult):
        self.advancedPage.mobileAppLoginDisplay(loginResult)

    def updateUPSName(self, param):
        try:
            self.client.queryRequest(Command.TARGET_SET_UPS_NAME, param)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def updateUPSNameStatusSlot(self, response):
        self.advancedPage.updateUPSNameStatusDisplay(response)

    def cloud_data_display_slot(self, cloud_data):
        try:
            self.advancedPage.cloud_data_display(cloud_data)
        except:
            traceback.print_exc(file=sys.stdout)

    def get_cloud_data_slot(self):
        self.client.queryRequest(Command.TARGET_CLOUD_DATA_DISPLAY, "")

    def cloud_verify_slot(self):
        self.client.queryRequest(Command.TARGET_CLOUD_VERIFY, "")

    def cloud_verify_result_slot(self, response):
        self.advancedPage.cloud_verify_result_display(response)