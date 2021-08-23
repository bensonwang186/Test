import traceback

import sys
import uuid

import platform
from PyQt5.QtCore import QObject, QTimer
import datetime, time

from model_Json.WebAppData import CloudLoginData
from model_Json.tables.Configuration import Configuration
from model_Json.tables.Account import Account
from model_Json import WebAppData
from controllers import MobileDataProvider, WebAppController
from major import Command
import json
from System import systemFunction, systemDefine
from views.Custom.ViewData import DeviceType, LoginType
from Utility import DataCryptor, Logger
from Utility.Scheduler import WebLoginThread


class AdvancedHandler(QObject):
    def __init__(self, server, device):
        super(AdvancedHandler, self).__init__()
        self.server = server
        self.device = device
        self.EmqMsgProvider = MobileDataProvider.EmqMsgProvider(device)
        self.FcmMsgProvider = MobileDataProvider.FcmMsgProvider(device)
        self.WebAppController = WebAppController.WebAppController(device)
        self.schedulerManager = self.device.schedulerManager
        self.daemonStartMobileLoginStart = False

        self.server.setShutdownTypeSignal.connect(self.setShutdownTypeConfigSlot)
        self.server.setSensitivitySignal.connect(self.setSensitivity)
        self.server.setMobileSolutionSignal.connect(self.setMobileSolutionEnableSlot)
        self.server.setMobileLoginSignal.connect(self.setMobileLoginSlot)
        self.server.updateUPSNameSignal.connect(self.updateUPSName)
        self.server.fetchMobileLoginSignal.connect(self.initMobileLoginSlot)
        self.server.fetch_cloud_data_signal.connect(self.fetch_cloud_data_slot)
        self.server.cloud_verify_signal.connect(self.cloud_verify_slot)
        # self.device.propertyFetcher.propertySignal.connect(self.daemonStartMobileLoginSlot)  #待DeviceMonitor取device SN後再進行login

        # DeviceMonitor取device SN -> DevicePropHandler更新isNoneSN -> mobile login
        self.device.propertyFetcher.mobileLoginSignal.connect(self.daemonStartMobileLoginSlot)

        # self.device.propertyFetcher.sendEmqStatusMsgSignal.connect(self.daemonStartMobileLoginSlot)

    def setShutdownTypeConfigSlot(self, param):
        try:
            config = Configuration()
            config.shutDownType = param

            self.device.dataSource.updateDeviceConfig(config)
        except Exception:
            Logger.LogIns().logger.info(traceback.format_exc())

    def setMobileSolutionEnableSlot(self, param):
        try:
            config = Configuration()
            config.mobileSolutionEnable = param

            self.device.dataSource.updateDeviceConfig(config)
            self.device.mobileSolutionEnable = param
            self.device.mobileLoginItem = WebAppData.AccountMobileLoginItem()

            if not param:
                self.device.mobileLoginItem.LoginType = LoginType.PowerPanelPersonalLogout.value
                self.device.mobileLoginItem.otp = self.device.otpKey
                self.EmqMsgProvider.stopSendEmqStatusMsgTimer()
                self.EmqMsgProvider.stop_after_event_timer()
                # self.EmqMsgProvider.stopSendApnsSilenceMsgTimer()
                self.EmqMsgProvider.sendEmqDeactivateMsg()
                # self.FcmMsgProvider.sendApnsDeactivateMsg()

                resp = self.WebAppController.Logout()
                if resp.Flag:
                    print("***[d-AdvancedHandler]Mobile solution logout successful at : " + str(datetime.datetime.now().time()) + "***")

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def setMobileLoginSlot(self, param):
        try:
            Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke setMobileLoginSlot() ***")
            cloud_data = CloudLoginData(param)
            print(cloud_data)

            # update Account table
            data = Account()
            data.accountId = cloud_data.account
            data.accountSecret = cloud_data.password
            if self.device.acode is not None and len(self.device.acode) > 0:
                data.acode = int(self.device.acode)
            self.device.dataSource.updateAppAccount(data)

            # update config table
            config = Configuration()
            config.mobileSolutionEnable = cloud_data.connect
            config.customUpsName = cloud_data.ups_name
            config.agree_policy = cloud_data.agree_policy
            self.device.dataSource.updateDeviceConfig(config)  # UPDATE
            self.device.mobileSolutionEnable = cloud_data.connect
            self.device.mobileLoginItem = WebAppData.AccountMobileLoginItem()
            self.device.customUPSName = cloud_data.ups_name

            # Login
            self.device.mobileLoginItem.Account = cloud_data.account

            config = self.device.dataSource.readActiveConfig()  # QUERY

            if systemFunction.stringIsNullorEmpty(cloud_data.password) is False:
                self.device.mobileLoginItem.Password = self.WebAppController.EncryptLoginPwd(config.pwdKey, cloud_data.password)

            self.device.mobileLoginItem.IP = ""
            self.device.mobileLoginItem.LoginType = LoginType.PowerPanelPersonalLogin.value
            self.device.mobileLoginItem.AddDeviceParam = self.NewDeviceParam(cloud_data.account)
            self.device.mobileLoginItem.AddDeviceParam.DeviceName = cloud_data.ups_name

            if self.device.isNoneSN:
                if self.device.altSN is not None and len(self.device.altSN) > 0:
                    self.device.mobileLoginItem.UpsSn = self.device.altSN
            else:
                self.device.mobileLoginItem.UpsSn = self.device.devicePropData.serialNumber.value

            # Login
            if cloud_data.connect:
                response = self.WebAppController.Login()
                Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke setMobileLoginSlot() cloud connect ***")
            else:
                self.setMobileSolutionEnableSlot(False)
                response = WebAppData.ResponseInfo()
                response.Flag = True
                Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke setMobileLoginSlot() connect disconnect ***")

            self.server.sendDataToClients(Command.TARGET_SET_MOBILE_LOGIN, response.toJson())

            self.EmqMsgProvider.sendEmqStatusMsg(True)

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    # 目前client socket等待daemon傳送數據時間為3秒
    # 為避免timeout將initMobileLoginSlot(處理畫面)與daemonStartMobileLoginSlot(傳送data)拆開
    # 順序: daemonStartMobileLoginSlot先, initMobileLoginSlot後

    def initMobileLoginSlot(self, clientConnection):  # 更新UI custom UPS name

        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke initMobileLoginSlot() ***")

        try:
            config = self.device.dataSource.readActiveConfig()
            account = self.device.dataSource.readAppAccount()

            cloud_data = CloudLoginData()
            cloud_data.account = account.accountId
            cloud_data.password = account.accountSecret
            if config.customUpsName is None or config.customUpsName is "":
                cloud_data.ups_name = self.device.customUPSName
            else:
                cloud_data.ups_name = config.customUpsName
            cloud_data.connect = config.mobileSolutionEnable
            cloud_data.agree_policy = config.agree_policy

            if systemFunction.stringIsNullorEmpty(account.accountId) is False and \
                    systemFunction.stringIsNullorEmpty(account.accountSecret) is False:
                cloud_data.verifiable = True

            cloud_json = cloud_data.to_json()
            self.server.sendToClient(Command.TARGET_CLOUD_DATA_DISPLAY, cloud_json, clientConnection)

            print("finish initMobileLoginSlot at " + str(datetime.datetime.now().time()))

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def daemonStartMobileLoginSlot(self, delaySec):   # daemon啟動時進行login

        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke daemonStartMobileLoginSlot() ***")
        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke daemonStartMobileLoginSlot() mobileLoginState: " + str(self.device.mobileLoginState) +" ***")
        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke daemonStartMobileLoginSlot() delaySec: " + str(delaySec) + " ***")
        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke daemonStartMobileLoginSlot() daemonStartMobileLoginStart: " + str(self.daemonStartMobileLoginStart) + " ***")

        if self.daemonStartMobileLoginStart is False:
            self.daemonStartMobileLoginStart = True
            Logger.LogIns().logger.info("***[d-AdvancedHandler] NEW WebLoginThread ***")
            self.schedulerManager.addWebLoginSchedule(WebLoginThread("WebLoginThread", delaySec, self))
            self.schedulerManager.startWebLoginSchedule()
            # self.ResetMobileLogin()

    def ResetMobileLogin(self):

        Logger.LogIns().logger.info("***[d-AdvancedHandler]invoke ResetMobileLogin() ***")

        try:
            config = self.device.dataSource.readActiveConfig()
            account = self.device.dataSource.readAppAccount()
            response = WebAppData.ResponseInfo()
            self.device.mobileLoginItem = WebAppData.AccountMobileLoginItem()

            if config is not None and config.mobileSolutionEnable is True and account is not None:

                self.device.mobileSolutionEnable = True
                self.device.mobileLoginItem.Account = account.accountId

                if systemFunction.stringIsNullorEmpty(account.accountSecret) is False:
                    self.device.mobileLoginItem.Password = self.WebAppController.EncryptLoginPwd(config.pwdKey,account.accountSecret)

                self.device.mobileLoginItem.IP = ""
                self.device.mobileLoginItem.LoginType = LoginType.PowerPanelPersonalLogin.value
                self.device.mobileLoginItem.AddDeviceParam = self.NewDeviceParam(account.accountId)
                self.device.mobileLoginItem.AddDeviceParam.DeviceName = config.customUpsName

                if self.device.isNoneSN:
                    if self.device.altSN is not None and len(self.device.altSN) > 0:
                        self.device.mobileLoginItem.UpsSn = self.device.altSN
                    else:
                        if account.acode is not None:
                            self.device.mobileLoginItem.UpsSn = "{0}_{1}_{2}_{3}".format(
                                account.acode,
                                self.device.devicePropData.modelName.value,
                                self.device.ProcessorId,
                                self.device.SMBiosUUID)
                else:
                    self.device.mobileLoginItem.UpsSn = self.device.devicePropData.serialNumber.value

                counter = 1
                response = WebAppData.ResponseInfo()

                Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin mobileLoginState: " + str(self.device.mobileLoginState) + "***")
                Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin deviceId: " + str(self.device.deviceId) + "***")
                Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin isLostCommunication: " + str(self.device.isLostCommunication) + "***")

                login_flag = False
                while login_flag is False and counter <= 10:  # 至多重連10次
                    response = self.WebAppController.Login()
                    Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin login counter: " + str(counter) + "***")
                    counter += 1
                    Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin login resp: " + str(response.Flag) + "***")
                    if response.Flag is True:
                        login_flag = True
                    else:  # 登入失敗10秒後重連
                        Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin login sleep 10 secs***")
                        time.sleep(10)

                Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin login resp: " + str(response.Message) + "***")

                if response.Flag and self.device.mobileLoginState is True:
                    Logger.LogIns().logger.info("***[d-AdvancedHandler]ResetMobileLogin login resp: start sendEmqStatusMsg()***")
                    login_flag = False
                    # self.EmqMsgProvider.sendEmqStatusMsg()
            else:
                self.device.mobileLoginState = False
                response.Flag = False  # login process failed
                response.Message = ""

            self.daemonStartMobileLoginStart = False
            # self.server.sendDataToClients(Command.TARGET_SET_MOBILE_LOGIN, response.toJson())
            # print("***do ResetMobileLogin successful at : " + str(datetime.datetime.now().time()) + "***")

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def setSensitivity(self, param):
        configData = self.device.deviceConfigure.configParam()
        configData.SET_VOLT_SENSITIVITY = 1
        configData.params.append(param)

        if self.device.deviceId != -1:
            flag = self.device.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)

            if flag:
                print("set Sensitivity success")
            else:
                print("set Sensitivity fail")

            return flag

    def updateUPSName(self, param):
        try:
            account = self.device.dataSource.readAppAccount()

            if account is not None:
                # self.device.checkDuplicateDeviceParam = WebAppData.CheckDuplicateDeviceParam()
                # self.device.checkDuplicateDeviceParam.AccountName = account.accountId
                # self.device.checkDuplicateDeviceParam.DeviceName = param
                # self.device.checkDuplicateDeviceParam.DeviceSn = self.device.devicePropData.serialNumber.value
                # response = self.WebAppController.checkDuplicateDeviceNameByAccount()

                # if response.Flag:
                self.device.updateDeviceParam = WebAppData.UpdateDeviceParam()
                self.device.updateDeviceParam.otp = self.device.otpKey
                self.device.updateDeviceParam.DeviceName = param

                if self.device.isNoneSN:
                    self.device.updateDeviceParam.DeviceSn = self.device.altSN
                else:
                    self.device.updateDeviceParam.DeviceSn = self.device.devicePropData.serialNumber.value

                response = self.WebAppController.updateUPSName()

            self.server.sendDataToClients(Command.TARGET_SET_UPS_NAME, response.toJson())

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def NewDeviceParam(self, accountId):
        addData = WebAppData.AccountMobileLoginItem.AddDeviceParam()
        addData.Account = accountId
        addData.UniqueId = ""
        addData.DeviceType = DeviceType.UPS.value
        # addData.DeviceName = self.device.customUPSName  # 是否upadte由webAP api判斷
        # addData.DeviceName = self.device.devicePropData.modelName.value
        addData.Model = self.device.devicePropData.modelName.value

        if self.device.isNoneSN:
            addData.DeviceSn = "{0}_{1}_{2}".format(
                self.device.devicePropData.modelName.value,
                self.device.ProcessorId,
                self.device.SMBiosUUID)
        else:
            addData.DeviceSn = self.device.devicePropData.serialNumber.value

        Logger.LogIns().logger.info("***[d-AdvancedHandler]NewDeviceParam addData.DeviceSn: " + str(addData.DeviceSn) + "***")
        Logger.LogIns().logger.info("***[d-AdvancedHandler]NewDeviceParam addData.DeviceName: " + str(addData.DeviceName) + "***")

        addData.DeviceOS = systemDefine.pppName + ' ' + systemDefine.pppeVersion

        osVer = platform.platform()
        osBit = platform.machine()

        addData.OSVersion = osVer + "-" + osBit
        addData.DeviceId = ""
        addData.CreateUser = accountId

        return addData

    def fetch_cloud_data_slot(self, client_connection):
        # 從資料庫拿資料
        config = self.device.dataSource.readActiveConfig()
        account = self.device.dataSource.readAppAccount()

        # 組成PPP Cloud畫面需要的資料
        cloud_data = CloudLoginData()
        cloud_data.account = account.accountId
        cloud_data.password = account.accountSecret
        if config.customUpsName is None:
            cloud_data.ups_name = self.device.customUPSName
        else:
            cloud_data.ups_name = config.customUpsName
        cloud_data.connect = config.mobileSolutionEnable
        cloud_data.agree_policy = config.agree_policy

        if systemFunction.stringIsNullorEmpty(account.accountId) is False and \
                systemFunction.stringIsNullorEmpty(account.accountSecret) is False:
            cloud_data.verifiable = True

        # 發送資料
        cloud_json = cloud_data.to_json()
        self.server.sendToClient(Command.TARGET_CLOUD_DATA_DISPLAY, cloud_json, client_connection)

    def cloud_verify_slot(self, client_connection):
        try:
           response = self.WebAppController.Login()

           if response.Flag:
               response.Message = "Verified Successfully"

           self.server.sendToClient(Command.TARGET_CLOUD_VERIFY, response.toJson(), client_connection)
        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
