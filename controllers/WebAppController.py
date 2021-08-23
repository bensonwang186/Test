import json
import traceback
from Utility import i18nTranslater, Logger, Scheduler, DataCryptor, RequestImp
from i18n import appLocaleData, i18nId
import sys
from model_Json import WebAppData, DevicePushMessageData
from controllers import MobileDataProvider, DeviceLogHelper
from System import systemFunction, systemDefine
from datetime import datetime, timedelta
import requests

class WebAppController:

    def __init__(self, device):
        self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorderFromDB().appLocale)
        self.device = device
        self.schedulerManager = self.device.schedulerManager
        self.fcmProvider = MobileDataProvider.FcmMsgProvider(device)
        self.EmqMsgProvider = MobileDataProvider.EmqMsgProvider(device)
        # self.EventMoble = EventsMobile.EventCloud(device)
        self.DeviceLogHelper = DeviceLogHelper.DevLogHelper(device)
        self.req = RequestImp.RequestImp()
        self.EmqEventProvider = MobileDataProvider.EmqEventProvider(device)

    def Login(self):
        responseInfo = WebAppData.ResponseInfo()

        try:
            Logger.LogIns().logger.info("***login-chk devicePropData sn: " + str(self.device.devicePropData.serialNumber.value) + "***")

            msg = self.device.mobileLoginItem

            Logger.LogIns().logger.info("***login-chk AddDeviceParam Model: " + str(msg.AddDeviceParam.Model) + "***")
            # msg.AddDeviceParam.DeviceSn = "" # debug

            if msg.AddDeviceParam and \
                    (systemFunction.stringIsNullorEmpty(msg.AddDeviceParam.Model)
                     or systemFunction.stringIsNullorEmpty(msg.AddDeviceParam.DeviceSn)):
                self.device.mobileLoginState = False
                responseInfo.Flag = False  # login process failed
                responseInfo.Message = i18nId.i18nId().Error_Occurred
            else:
                jsonMsg = msg.toJson()
                url = systemDefine.LOGIN_API_URL

                print(jsonMsg)
                headers = {'Content-type': 'application/json', 'Connection': 'close'}
                response = self.req.post(url, data=jsonMsg, headers=headers)

                print(response)

                result = json.loads(response.text)
                if response.status_code == 200 and result["Flag"]:
                    self.device.mobileLoginState = True
                    self.device.topicId = result["TopicId"]
                    self.device.freqConstant = int(result["freq_constant"])
                    self.device.freqAppAct = int(result["freq_app_act"])
                    self.device.acode = result["acode"]
                    self.device.otpKey = result["OtpKey"]

                    if self.device.freqConstant > 0:
                        self.device.EmqLostCommunicationMsgTimesLimit = int(
                            result["dur_stat_lost"]) / self.device.freqConstant

                    if self.device.freqAppAct > 0:
                        self.device.APNsLostCommunicationMsgTimesLimit = int(
                            result["dur_apn_lost"]) / self.device.freqAppAct

                    if self.device.isNoneSN:
                        self.device.altSN = "{0}_{1}_{2}_{3}".format(
                            self.device.acode,
                            self.device.devicePropData.modelName.value,
                            self.device.ProcessorId,
                            self.device.SMBiosUUID)
                        self.device.upsSN_Temp = self.device.altSN
                        mapping_sn = self.device.altSN
                    else:
                        mapping_sn = self.device.devicePropData.serialNumber.value

                    Logger.LogIns().logger.info("***login-chk altSN: " + str(self.device.altSN) + "***")
                    Logger.LogIns().logger.info("***login-chk mapping_sn: " + str(mapping_sn) + "***")

                    devicesInfor = result["DevicesInfor"]
                    device = next((f for f in devicesInfor if f["DeviceSN"] == mapping_sn),None)

                    if device is not None:
                        self.device.customUPSName = device["DeviceName"]
                        self.device.dcode = device["Id"]

                    Logger.LogIns().logger.info("***login-chk customUPSName: " + str(self.device.customUPSName) + "***")

                    # Read cloud events parameters:
                    self.device.cloudEvtDur = int(result["evt_log_dur"])

                    evtDisplayStr = result["evt_display"]
                    if evtDisplayStr is not None and len(evtDisplayStr) > 0:
                        self.device.cloudEvtDisplay = systemFunction.hexStringToBoolArray(evtDisplayStr)

                    evtLogSendStr = result["evt_log_send"]
                    if evtLogSendStr is not None and len(evtLogSendStr) > 0:
                        self.device.cloudEvtSend = systemFunction.hexStringToBoolArray(evtLogSendStr)

                    responseInfo.Message = "Success"
                    responseInfo.Flag = True  # login process succeed

                else:
                    self.device.mobileLoginState = False
                    responseInfo.Flag = False  # login process failed
                    responseInfo.Message = i18nId.i18nId().Cloud_Incorrect_Account_or_Password

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            responseInfo.Flag = False  # login process error
            responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Error_Occurred)

        return responseInfo

    def Logout(self):
        responseInfo = WebAppData.ResponseInfo()

        try:
            msg = self.device.mobileLoginItem
            jsonMsg = msg.toJson()
            url = systemDefine.LOGOUT_API_URL

            print(jsonMsg)
            headers = {'Content-type': 'application/json'}
            response = self.req.post(url, data=jsonMsg, headers=headers)
            print(response)

            result = json.loads(response.text)

            if result["Flag"]:
                self.device.mobileLoginState = False
                responseInfo.Flag = True  # logout process succeed
                responseInfo.Message = ''
            else:
                responseInfo.Flag = False  # logout process failed
                responseInfo.Message = 'logout process failed'

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            responseInfo.Flag = False  # logout process error
            responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Error_Occurred)

        return responseInfo

    def updateUPSName(self):
        responseInfo = WebAppData.ResponseInfo()

        try:
            msg = self.device.updateDeviceParam
            jsonMsg = msg.toJson()
            url = systemDefine.UPDATE_DEVICE_INFOR_API_URL

            print(jsonMsg)
            headers = {'Content-type': 'application/json'}
            response = self.req.post(url, data=jsonMsg, headers=headers)
            print(response)

            if response.status_code == 401: # if otp expired
                loginResp = self.WebAppController.Login()
                if loginResp.Flag:
                    response = requests.post(url, data=jsonMsg, headers=headers)
                    print(response)

            result = json.loads(response.text)

            if response.status_code == 200 and result["Flag"]:
                responseInfo.Flag = True  # update successful
                responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Update_Success)
                self.device.customUPSName = msg.DeviceName
            else:
                responseInfo.Flag = False  # update failed
                responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Update_Failed)
        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            responseInfo.Flag = False  # update failed
            responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Error_Occurred)

        return responseInfo

    def checkDuplicateDeviceNameByAccount(self):
        responseInfo = WebAppData.ResponseInfo()

        try:
            msg = self.device.checkDuplicateDeviceParam
            jsonMsg = msg.toJson()
            url = systemDefine.CHECK_DUPLICATE_DEVICE_NAME_API_URL

            print(jsonMsg)
            headers = {'Content-type': 'application/json'}
            response = self.req.post(url, data=jsonMsg, headers=headers)
            print(response)

            result = json.loads(response.text)

            if result["Flag"]:
                responseInfo.Flag = True  # true means no duplicate device name
                responseInfo.Message = ''
            else:
                responseInfo.Flag = False  # false means exists duplicate device name
                responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Duplicate_device_name)

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            responseInfo.Flag = False  # update failed
            responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Error_Occurred)

        return responseInfo

    def addDeviceLogApp(self, dcode, endDate):
        responseInfo = WebAppData.ResponseInfo()

        try:
            startDate = endDate - timedelta(seconds=self.device.cloudEvtDur)
            logs = self.device.dataSource.deviceLogQuery(startDate, endDate, dcode)

            if logs != None and len(logs) > 0:

                dsn = logs[0].dsn

                # remove redundant attribute
                for log in logs:
                    del log.id
                    del log.dsn
                    del log.LocalTime
                    del log.dcode


            param = WebAppData.AddDeviceLogParam()
            param.dsn = dsn
            param.logs = logs
            paramJson = param.toJson()
            url = systemDefine.ADD_DEVICE_LOG_APP_API_URL

            Logger.LogIns().logger.info("***[WebAppController] addDeviceLogApp() nginx API request = {0} ***".format(str(paramJson)))

            # print(paramJson)
            headers = {'Content-type': 'application/json'}
            response = self.req.post(url, data=paramJson, headers=headers)
            # print(response)

            Logger.LogIns().logger.info("***[WebAppController] addDeviceLogApp() nginx API response = {0} ***".format(str(response.text)))

            result = json.loads(response.text)

            Logger.LogIns().logger.info("***[WebAppController] addDeviceLogApp() nginx API result = {0} ***".format(str(result)))

            if result["result"]:
                responseInfo.Flag = True  # true means no duplicate device name
                responseInfo.Message = ''
            else:
                responseInfo.Flag = False  # false means exists duplicate device name
                responseInfo.Message = "add device log app failed"

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            responseInfo.Flag = False  # update failed
            responseInfo.Message = self.i18nTranslater.getTranslateString(i18nId.i18nId().Error_Occurred)

        return responseInfo

    def saveAndSendDeviceLog(self, useThread):  # useThread: True用thread來呼叫nginx API, False則否

        try:
            fetchData = DevicePushMessageData.SilenceMessage()
            fetchData.Type = self.device.devicePushSilenceMsg.Type
            fetchData.Dev = self.device.devicePushSilenceMsg.Dev
            fetchData.Event = self.device.devicePushSilenceMsg.Event
            fetchData.PowSour = self.device.devicePushSilenceMsg.PowSour
            fetchData.InVolt = self.device.devicePushSilenceMsg.InVolt
            fetchData.InFreq = self.device.devicePushSilenceMsg.InFreq
            fetchData.BatCap = self.device.devicePushSilenceMsg.BatCap
            fetchData.BatRun = self.device.devicePushSilenceMsg.BatRun
            fetchData.OutVolt = self.device.devicePushSilenceMsg.OutVolt
            fetchData.OutFreq = self.device.devicePushSilenceMsg.OutFreq
            fetchData.OutCur = self.device.devicePushSilenceMsg.OutCur
            fetchData.Load = self.device.devicePushSilenceMsg.Load
            fetchData.OutSta = self.device.devicePushSilenceMsg.OutSta
            fetchData.BatSta = self.device.devicePushSilenceMsg.BatSta
            fetchData.BatVolt = self.device.devicePushSilenceMsg.BatVolt
            fetchData.Model = self.device.devicePushSilenceMsg.Model
            fetchData.FV = self.device.devicePushSilenceMsg.FV
            fetchData.LP = self.device.devicePushSilenceMsg.LP
            fetchData.RatPow = self.device.devicePushSilenceMsg.RatPow
            fetchData.Out = self.device.devicePushSilenceMsg.Out
            fetchData.NclOut = self.device.devicePushSilenceMsg.NclOut
            fetchData.SN = self.device.devicePushSilenceMsg.SN
            fetchData.countrySelection = self.device.devicePushSilenceMsg.countrySelection
            fetchData.energyCost = self.device.devicePushSilenceMsg.energyCost
            fetchData.co2Emitted = self.device.devicePushSilenceMsg.co2Emitted
            fetchData.unit = self.device.devicePushSilenceMsg.unit
            fetchData.statistic = self.device.devicePushSilenceMsg.statistic
            fetchData.powerProblem = self.device.devicePushSilenceMsg.powerProblem
            fetchData.upsName = self.device.devicePushSilenceMsg.upsName
            fetchData.upsState = self.device.devicePushSilenceMsg.upsState
            fetchData.tstamp = self.device.devicePushSilenceMsg.tstamp
            fetchData.InSta = self.device.devicePushSilenceMsg.InSta

            fetchData.BatTRes = self.device.devicePushSilenceMsg.BatTRes
            fetchData.BatTDate = self.device.devicePushSilenceMsg.BatTDate
            fetchData.BatTFrom = self.device.devicePushSilenceMsg.BatTFrom
            fetchData.SysTemp = self.device.devicePushSilenceMsg.SysTemp

            fetchData.EventCode = self.device.devicePushSilenceMsg.EventCode
            fetchData.EventCodeRestore = self.device.devicePushSilenceMsg.EventCodeRestore
            fetchData.EventCodeNew = self.device.devicePushSilenceMsg.EventCodeNew

            currentEvents = self.device.cloudEvents.copy()  # assign cloudEvents to new list
            currentEventStatData = self.device.eventStatData.copy()

            Logger.LogIns().logger.info("***[WebAppController] saveAndSendDeviceLog() currentEvents: {0} ***".format(str(currentEvents)))
            Logger.LogIns().logger.info("***[WebAppController] saveAndSendDeviceLog() currentEventStatData: {0} ***".format(str(currentEventStatData)))

            self.sendEmqMsg(fetchData, currentEvents, useThread)  # new thread send EMQ msg
            # self.sendFcmAlertMsg()
            result = self.DeviceLogHelper.saveLogs(fetchData, currentEvents, currentEventStatData)  # save device_log to DB

            if result is not None:
                Logger.LogIns().logger.info("***[WebAppController] saveAndSendDeviceLog() Save Device Log result: {0} at {1}***".format(str(result[0]), str(result[1])))
                self.sendCloudEvent(result, currentEvents, useThread)  # new thread send logs to nginx

            # Logger.LogIns().logger.info("***[Monitor] cloudEventsTemp: {0} ***".format(str(cloudEventsTemp)))
            # Logger.LogIns().logger.info("***[Monitor] device cloudEventsTemp: {0} ***".format(str(self.device.cloudEventsTemp)))
            # if clearFlag:
            #     self.device.cloudEventsTemp = []  # clear

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def sendFcmAlertMsg(self):
        try:
            Logger.LogIns().logger.info("***[WebAppController] sendFcmAlertMsg() messageTitle value = {0} ***".format(str(self.device.devicePushAlertMsg.messageTitle)))
            Logger.LogIns().logger.info("***[WebAppController] sendFcmAlertMsg() messageBody value = {0} ***".format(str(self.device.devicePushAlertMsg.messageBody)))
            if self.device.devicePushAlertMsg.messageTitle is not None and self.device.devicePushAlertMsg.messageBody is not None:
                self.fcmProvider.doSendApnsAlertMsg()
                self.device.devicePushAlertMsg = DevicePushMessageData.AlertMessage()  # clear
        except Exception as e:
                Logger.LogIns().logger.info(traceback.format_exc())

    def sendEmqMsg(self, currentStatusMsg, currentEvents, useThread):
        Logger.LogIns().logger.info("***[WebAppController] sendEmqMsg() cloudEvents value = {0} ***".format(str(currentEvents)))
        if len(currentEvents) > 0:
            try:
                currentStatusMsg.Event = self.EmqMsgProvider.EventMoble.GetEventObj(currentEvents)

                if useThread:
                    self.schedulerManager.addEmqMsgSchedule(Scheduler.EmqMsgThread("EmqMsgThread", 0, self.EmqEventProvider, currentStatusMsg))
                    self.schedulerManager.startEmqMsgSchedule()
                else:
                    self.EmqEventProvider.doSendCurrentEmqStatusMsg(currentStatusMsg)

                # clear
                self.device.devicePushSilenceMsg.Event = DevicePushMessageData.SilenceMessage.Event()
                self.device.devicePushSilenceMsg.BatTRes = None
                self.device.devicePushSilenceMsg.BatTDate = None
                self.device.devicePushSilenceMsg.BatTFrom = None
                self.device.devicePushSilenceMsg.EventCode = None
                self.device.devicePushSilenceMsg.EventCodeRestore = None
                self.device.devicePushSilenceMsg.EventCodeNew = None
            except Exception as e:
                Logger.LogIns().logger.info(traceback.format_exc())

    def sendCloudEvent(self, saveLogResp, currentEvents, useThread):
        try:
            # if cloud events, invoke Nginx API to save device logs
            Logger.LogIns().logger.info("***[WebAppController] sendCloudEvent() cloudEvents value = {0} ***".format(str(currentEvents)))
            if len(currentEvents) > 0:

                # 確認事件是否需要送至Cloud Server
                # 只要sendCheckArr包含True: 送出device logs
                sendCheckArr = []
                for item in currentEvents:
                    chkFlag = False
                    if item in self.device.cloudEvtSend:
                        chkFlag = self.device.cloudEvtSend[item]

                    sendCheckArr.append(chkFlag)

                # satisfy conditions:  mobile solution enable, login success and dcode exist
                if True in sendCheckArr and self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                        and self.device.topicId is not None and self.device.dcode is not None:

                    if saveLogResp[0]:
                        endDate = saveLogResp[1]
                    else:
                        endDate = systemFunction.getDatetimeNonw()

                    dcode = self.device.dcode

                    # invoke Nginx API to save device logs
                    if useThread:
                        self.schedulerManager.addDeviceLogSchedule(Scheduler.DeviceLogThread("DeviceLogThread", 6, self, dcode, endDate))
                        self.schedulerManager.startDeviceLogSchedule()
                    else:
                        response = self.addDeviceLogApp(dcode, endDate)

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            traceback.print_exc(file=sys.stdout)

    def printLog(self, name, msg):
        Logger.LogIns().logger.info("***[WebAppController] printLog() {0} value = {1} ***".format(str(name), str(msg)))

    def EncryptLoginPwd(self, key, password):
        try:
            cryptor = DataCryptor.Cryptor()
            decryptedPWD = cryptor.decToString(password)
            PWDKey = cryptor.decToString(key)
            newEncryptedPWD = systemFunction.md5Hash(decryptedPWD) + systemFunction.sha512Hash(PWDKey, decryptedPWD)
            return newEncryptedPWD.upper()

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())
            return None


