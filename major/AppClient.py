import csv
import json
import os
import subprocess
import threading
import traceback
import sys
import platform
import re
from i18n import appLocaleData
from datetime import datetime
from PyQt5.QtCore import QDataStream, QIODevice, pyqtSignal, QObject, QByteArray, QTimer
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
from PyQt5.QtWidgets import QApplication
from Utility import Logger
from major import Command, Verification
from model_Json import DeviceStatusData, DevicePropertiesData
from model_Json.tables.Configuration import Configuration as Configuration
from model_Json.tables.EmailNotification import EmailNotification as EmailNotification
from model_Json.tables.EnergyCost import EnergyCost as EnergyCost
from model_Json.tables.EnergyCost import EnergySetting as EnergySetting
from model_Json.tables.Schedule import Schedule as Schedule
from model_Json.WebAppData import ResponseInfo as ResponseInfo, CloudLoginData
from System import loggerSetting

class Client(QObject):

    deviceStatusUpdateSignal = pyqtSignal(object)
    notificationEmailUpdataSignal = pyqtSignal(object, object)
    updateConfigSettingSignal = pyqtSignal(object)
    updateEventLogSignal = pyqtSignal(object)
    updatePropertySignal = pyqtSignal(object)
    disableConfigureSignal = pyqtSignal(object)
    scheduleSettingUpdateSignal = pyqtSignal(object)
    energySettingsUpdateSignal = pyqtSignal(object)
    setEnergySettingResultSignal = pyqtSignal(object)
    serverDisconnected = pyqtSignal(object)
    stopProgramSignal = pyqtSignal(object)
    energyReportingSignal = pyqtSignal(object)
    setVerifyResultSignal = pyqtSignal(object)
    sendTestEmailResultSignal = pyqtSignal(object)
    oathExchangedResultSignal = pyqtSignal(object)
    showAppDisplaySignal = pyqtSignal()
    mobileAppLoginSignal = pyqtSignal(object)
    updateUPSNameSignal = pyqtSignal(object)
    updateEventLogPageSignal = pyqtSignal(object)
    clearEventLogsSignal = pyqtSignal(object)
    updateClearEventLogsSignal = pyqtSignal(object)
    update_status_signal = pyqtSignal(object)
    update_dialog_result_signal = pyqtSignal(object)
    cloud_data_display_signal = pyqtSignal(object)
    cloud_verify_result_signal = pyqtSignal(object)

    def __init__(self, daemonStatus):
        super(Client, self).__init__()
        self.tcpSocket = QTcpSocket()
        self.nextBlockSize = 0
        self.isConnected = False
        self.isVerified = False
        self.isInitial = False
        self.daemonStatus = daemonStatus

        self.tcpSocket.readyRead.connect(self.readFromServer)
        self.tcpSocket.connected.connect(self.toogleConnectedState)
        self.tcpSocket.disconnected.connect(self.handleDisconnect)
        self.tcpSocket.error.connect(self.serverHasError)

        self.sendLock = threading.Lock()
        Logger.LogIns().logger.info("[Client] Start finding server socket")
        self.processingFinder()

        # send any message you like it could come from a widget text.

    def processingFinder(self):
        self.t0 = QTimer()
        self.t1 = QTimer()
        self.t2 = QTimer()
        self.chk = Checker(self, self.t0, self.t1, self.t2)

        self.t0.timeout.connect(self.chk.tryConnect)
        self.t0.start(5000)
        self.t1.timeout.connect(self.chk.verify)
        self.t2.timeout.connect(self.chk.fetchProperties)

    def toogleConnectedState(self):
        Logger.LogIns().logger.info("[Client] toogleConnectedState")
        self.killDuplicateApp()
        self.isConnected = True
        self.daemonStatus.isDaemonStarted = True

        # Daemon斷訊時更新UI與tray狀態
        self.daemonStatus.daemonStatusUpdateSignal.emit(self.daemonStatus)

    def getCurrentUserProcesses(self):
        if platform.system() == 'Windows':
            CREATE_NO_WINDOW = 0x08000000  # hide console

            # by windows CMD
            csv_output = subprocess.check_output(
                ["tasklist", "/FI", "USERNAME eq {}".format(os.getenv("USERNAME")), "/FI",
                 "ImageName eq {}".format("PowerPanel Personal.exe"), "/FO", "CSV"],
                creationflags=CREATE_NO_WINDOW).decode("ascii", "ignore")

            cr = csv.reader(csv_output.splitlines())
            next(cr)  # skip title lines
            # return {int(row[1]): row[0] for row in cr}
            return list(int(row[1]) for row in cr)

        # To be refactoring. 改成posix 指令來確認process已存在
        elif platform.system() == 'Darwin':
            command = "ps aux | grep -i 'powerpanel personal$'"
            result = subprocess.check_output(command, shell=True).decode("utf-8")
            resultList = result.splitlines()
            processList = []
            processIdList = []
            for index in range(len(resultList)):
                if "grep" not in resultList[index]:
                    processList.append(re.sub(r"\s+", ",", resultList[index]))
            cr = csv.reader(processList, delimiter=',')
            for row in cr:
                processIdList.append(row[1])
            return processIdList

    def killDuplicateApp(self):
        Logger.LogIns().logger.info("[Client] Kill duplicate client app")
        try:
            currentUserProcesses = self.getCurrentUserProcesses()  # get current user processes pid list
            # psutilProcess = list(filter(lambda x: "PowerPanel Personal.exe" in x.info['name'] and x.info['pid']in currentUserProcesses,
            #                             psutil.process_iter(attrs=['pid', 'name'])))  # select process by name
            if platform.system() == 'Windows':
                if len(currentUserProcesses) >= 2:
                    sys.exit(0)
            elif platform.system() == 'Darwin':
                if len(currentUserProcesses) >= 2:
                    sys.exit(0)

        except Exception as e:
            Logger.LogIns().logger.info(e)
            traceback.print_exc(file=sys.stdout)

    def start(self):
        try:
            self.makeRequest()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def vv(self):
        # # do verify
        verify = Verification.Verifier()
        code = verify.genEncode()
        self.queryRequest(Command.TARGET_VERIFY, verify.toJson())

    def makeRequest(self):
        HOST = '127.0.0.1'
        PORT = 31111
        self.tcpSocket.connectToHost(HOST, PORT)

    def divideContent(self, command, text):
        try:
            left = "{"
            right = "}"
            if command == Command.TARGET_ENERGY_SETTINGS \
                    or command == Command.TARGET_SCHEDULE \
                    or command == Command.TARGET_ENERGY_REPORT \
                    or command == Command.TARGET_NOTIFICATION_EMAIL \
                    or command == Command.TARGET_EVENT_LOG\
                    or command == Command.TARGET_EVENT_LOG_PAGE:
                left = "["
                right = "]"
            dataStartIndex = text.find(command + left) + len(command)
            dataEndIndex = text.find(right + command) + 1
            if dataStartIndex != -1 and dataEndIndex != 0:
                content = text[dataStartIndex:dataEndIndex]
            return content
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def readFromServer(self):
        try:
            # self.checkReadBufferLimitReached()
            self.nextBlockSize = 0
            Logger.LogIns().logger.info("[Client] Receive socket data  signal")
            Logger.LogIns().logger.info("[Client] Receive socket data signal self.nextBlockSize: " + str(self.nextBlockSize))
            Logger.LogIns().logger.info(
                "[Client] Receive socket data signal self.tcpSocket.bytesAvailable: " + str(
                    self.tcpSocket.bytesAvailable()))
            stream = QDataStream(self.tcpSocket)
            stream.setVersion(QDataStream.Qt_5_0)

            command_array = []
            buffer_size = self.tcpSocket.bytesAvailable()

            if buffer_size > 0:
                text_from_server_byte = stream.readRawData(buffer_size)
                text_from_server = text_from_server_byte.decode("utf-8")
                command_array = self.get_command_array(text_from_server)

            for command in command_array:
                self.execute_command(command)

        except Exception:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)

    def execute_command(self, textFromServer):
        if Command.TARGET_STATUS not in textFromServer:
            Logger.LogIns().logger.info("[Client] Receive socket data: " + str(textFromServer))

        if textFromServer is not "":

            if Command.TARGET_STATUS in textFromServer:
                # 初始化完才會status，必免在initial時收到status會額外發送其他非initail的target給daemon造成dead lock
                Logger.LogIns().logger.info("[Client] receive status")
                Logger.LogIns().logger.info("[Client] is initial: " + str(self.isInitial))
                if self.isInitial:
                    Logger.LogIns().logger.info("[Client] Already Initial")
                    content = self.divideContent(Command.TARGET_STATUS, textFromServer)
                    if content:
                        Logger.LogIns().logger.info("[Client] Parse status")
                        deviceStatus = DeviceStatusData.DeviceStatus(content)
                        Logger.LogIns().logger.info("[Client] Parse status done")
                        self.deviceStatusUpdateSignal.emit(deviceStatus)
                        Logger.LogIns().logger.info("[Client] emit status done")
                else:
                    Logger.LogIns().logger.info("[Client] Not yet Initial")
            if Command.TARGET_NOTIFICATION_EMAIL in textFromServer:
                content = self.divideContent(Command.TARGET_NOTIFICATION_EMAIL, textFromServer)
                if content:
                    jsonObject = json.loads(content)
                    emailNotification = EmailNotification(jsonObject[0])
                    self.notificationEmailUpdataSignal.emit(emailNotification, jsonObject[1])
            if Command.TARGET_CONFIG in textFromServer:
                try:
                    content = self.divideContent(Command.TARGET_CONFIG, textFromServer)
                    if content:
                        configuration = Configuration(content)
                        self.updateConfigSettingSignal.emit(configuration)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
            if Command.TARGET_PROPERTY in textFromServer:
                content = self.divideContent(Command.TARGET_PROPERTY, textFromServer)
                if content:
                    devicePropertiesData = DevicePropertiesData.DevicePropertiesData(content)
                    self.updatePropertySignal.emit(devicePropertiesData)
            if Command.TARGET_ENERGY_SETTINGS in textFromServer:
                content = self.divideContent(Command.TARGET_ENERGY_SETTINGS, textFromServer)
                if content:
                    displayDic2 = json.loads(content)
                    energySetting = EnergySetting(displayDic2[0])
                    energyCostList = []
                    for costString in displayDic2[1]:
                        energyCostList.append(EnergyCost(costString))
                    self.energySettingsUpdateSignal.emit((energySetting, energyCostList))
            if Command.TARGET_EVENT_LOG in textFromServer:
                try:
                    content = self.divideContent(Command.TARGET_EVENT_LOG, textFromServer)
                    self.updateEventLogSignal.emit(content)
                    print(content)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
            if Command.TARGET_EVENT_LOG_PAGE in textFromServer:
                try:
                    content = self.divideContent(Command.TARGET_EVENT_LOG_PAGE, textFromServer)
                    self.updateEventLogPageSignal.emit(content)
                    print(content)
                except Exception:
                    traceback.print_exc(file=sys.stdout)

            if Command.TARGET_CLEAR_ALL_EVENTLOGS in textFromServer:
                try:
                    content = self.divideContent(Command.TARGET_CLEAR_ALL_EVENTLOGS, textFromServer)
                    if 'true' in content:
                        self.updateClearEventLogsSignal.emit(True)
                    else:
                        self.updateClearEventLogsSignal.emit(False)
                    print("CLEAR_ALL_EVENTLOGS resp: {0}".format(content))
                except Exception:
                    traceback.print_exc(file=sys.stdout)

            if Command.TARGET_SCHEDULE in textFromServer:
                content = self.divideContent(Command.TARGET_SCHEDULE, textFromServer)
                if content:
                    displayDic2 = json.loads(content)
                    print(displayDic2)
                    displayDic3 = []
                    for key in displayDic2[0]:
                        print(key)
                        displayDic3.append(Schedule(key))
                    try:
                        if displayDic2[1] is None:
                            stopData = None
                        else:
                            stopData = Schedule(displayDic2[1])
                    except Exception:
                        pass

                    try:
                        if displayDic2[2] is None:
                            startData = None
                        else:
                            startData = Schedule(displayDic2[2])
                    except Exception:
                        pass

                    try:
                        self.scheduleSettingUpdateSignal.emit((displayDic3, stopData, startData))
                    except Exception:
                        Logger.LogIns().logger.error(traceback.print_exc())
                        traceback.print_exc(file=sys.stdout)

            if Command.TARGET_SET_VERIFY_EMAIL in textFromServer:
                content = self.divideContent(Command.TARGET_SET_VERIFY_EMAIL, textFromServer)
                if content:
                    contentObject = json.loads(content)
                    result = contentObject["param"]
                    self.setVerifyResultSignal.emit(result)

            if Command.TARGET_SET_TEST_EMAIL in textFromServer:
                content = self.divideContent(Command.TARGET_SET_TEST_EMAIL, textFromServer)
                if content:
                    contentObject = json.loads(content)
                    result = contentObject["param"]
                    self.sendTestEmailResultSignal.emit(result)

            if Command.TARGET_EXCHANGE_OAUTH in textFromServer:
                content = self.divideContent(Command.TARGET_EXCHANGE_OAUTH, textFromServer)
                if content:
                    contentObject = json.loads(content)
                    result = contentObject["param"]
                    self.oathExchangedResultSignal.emit(result)

            if Command.TARGET_SET_ENERGY_SETTINGS_RESULT in textFromServer:
                content = self.divideContent(Command.TARGET_SET_ENERGY_SETTINGS_RESULT, textFromServer)
                if content:
                    contentObject = json.loads(content)
                    result = contentObject["param"]
                    self.setEnergySettingResultSignal.emit(result)

            if Command.TARGET_ENERGY_REPORT in textFromServer:
                content = self.divideContent(Command.TARGET_ENERGY_REPORT, textFromServer)
                if content:
                    contentObject = json.loads(content)
                    energySetting = EnergySetting(contentObject[3])
                    self.energyReportingSignal.emit(
                        (contentObject[0], contentObject[1], contentObject[2], energySetting))

            if Command.TARGET_SHOW_APP_DISPLAY in textFromServer:
                content = self.divideContent(Command.TARGET_SHOW_APP_DISPLAY, textFromServer)
                if content:
                    self.showAppDisplaySignal.emit()

            if Command.TARGET_VERIFY in textFromServer:
                now = datetime.datetime.now()

                for i in range(0, 5):
                    d1 = now - datetime.timedelta(seconds=i)
                    data = d1.strftime("%Y-%m-%d %H:%M:%S")

                    content = self.divideContent(Command.TARGET_VERIFY, textFromServer)
                    if content:
                        verify = Verification.Verifier(content)
                        if verify.verify(data, verify.sha1):
                            self.isConnected = True

            Logger.LogIns().logger.info("[Client] Handle receive socket data done ")
            if Command.TARGET_STOP in textFromServer:
                Logger.LogIns().logger.error("[Client] Handle receive socket data error ")
                Logger.LogIns().logger.error(traceback.print_exc())
                self.stopProgramSignal.emit()

            if Command.TARGET_MOBILE_LOGIN in textFromServer:
                content = self.divideContent(Command.TARGET_MOBILE_LOGIN, textFromServer)

                if content:
                    responseInfo = ResponseInfo(content)
                    self.mobileAppLoginSignal.emit(responseInfo)

            if Command.TARGET_SET_MOBILE_LOGIN in textFromServer:
                content = self.divideContent(Command.TARGET_SET_MOBILE_LOGIN, textFromServer)

                if content:
                    responseInfo = ResponseInfo(content)
                    self.mobileAppLoginSignal.emit(responseInfo)

            if Command.TARGET_SET_UPS_NAME in textFromServer:
                content = self.divideContent(Command.TARGET_SET_UPS_NAME, textFromServer)

                if content:
                    responseInfo = ResponseInfo(content)
                    self.updateUPSNameSignal.emit(responseInfo)

                self.stopProgramSignal.emit(True)
            if Command.TARGET_UPDATE_STATUS in textFromServer:
                content = self.divideContent(Command.TARGET_UPDATE_STATUS, textFromServer)

                if content:
                    responseInfo = ResponseInfo(content)
                    self.update_status_signal.emit(responseInfo)

            if Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT in textFromServer:
                content = self.divideContent(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, textFromServer)

                if content:
                    contentObject = json.loads(content)
                    result = contentObject["param"]
                    self.update_dialog_result_signal.emit(result)

            if Command.TARGET_CLOUD_DATA_DISPLAY in textFromServer:
                content = self.divideContent(Command.TARGET_CLOUD_DATA_DISPLAY, textFromServer)

                if content:
                    cloud_data = CloudLoginData(content)
                    self.cloud_data_display_signal.emit(cloud_data)

            if Command.TARGET_CLOUD_VERIFY in textFromServer:
                content = self.divideContent(Command.TARGET_CLOUD_VERIFY, textFromServer)

                if content:

                    result = ResponseInfo(content)
                    self.cloud_verify_result_signal.emit(result)

    def checkReadBufferLimitReached(self):
        try:
            Logger.LogIns().logger.info("[Client] tcpSocket.readBufferSize(): " + str(self.tcpSocket.readBufferSize()))
            Logger.LogIns().logger.info("[Client] tcpSocket.bytesAvailable(): " + str(self.tcpSocket.bytesAvailable()))
            self.readBufferSize = self.tcpSocket.readBufferSize()  # Current max read buffer size.
            self.flag = False  # flag for changing max read buffer size.
            self.isReadBufferLimitReached = False

            if self.readBufferSize <= self.tcpSocket.bytesAvailable():
                self.isReadBufferLimitReached = True
            elif self.isReadBufferLimitReached:
                Logger.LogIns().logger.info("[Client] isReadBufferLimitReached: " + str(True))
                if self.flag:

                    self.readBufferSize += 1
                    self.flag = not self.flag

                else:

                    self.readBufferSize -= 1
                    self.flag = not self.flag

                self.tcpSocket.setReadBufferSize(self.readBufferSize)
                self.isReadBufferLimitReached = False
        except Exception:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)

    def queryRequest(self, command, param=None, isWaitReady=False):
        isOk = False
        try:
            Logger.LogIns().logger.info("[Client] ask send lock")
            self.sendLock.acquire()
            # print("ask:"+command)

            Logger.LogIns().logger.info("[Client] get send lock ready to send")
            request = QByteArray()
            stream = QDataStream(request, QIODevice.WriteOnly)
            stream.setVersion(QDataStream.Qt_5_0)
            Logger.LogIns().logger.info("[Client] send1")
            if Command == Command.TARGET_SET_SCHEDULE or Command == Command.TARGET_VERIFY or Command == Command.TARGET_ENERGY_REPORT or Command == Command.TARGET_EVENT_LOG_PAGE:
                Logger.LogIns().logger.info("[Client] send2")
                content = self.composed_content_data(command, param)
                byte_content = content.encode("utf-8")
                stream.writeRawData(byte_content)
            else:
                if param == None:
                    Logger.LogIns().logger.info("[Client] send3")
                    content = self.composed_content_data(command, "")
                    byte_content = content.encode("utf-8")
                    stream.writeRawData(byte_content)
                else:
                    Logger.LogIns().logger.info("[Client] send4")
                    configObj = ConfigObj()
                    configObj.param = param
                    print(configObj.toJson())
                    content = self.composed_content_data(command, configObj.toJson())
                    byte_content = content.encode("utf-8")
                    stream.writeRawData(byte_content)
            # resetResult = stream.device().reset()
            seekResult = stream.device().seek(0)
            Logger.LogIns().logger.info(
                "[Client] Send to Server: " + str(request))
            self.tcpSocket.write(request)
            self.tcpSocket.flush()
            if isWaitReady:
                Logger.LogIns().logger.info("[Client] wait for ready read")
                isOk = self.tcpSocket.waitForReadyRead(msecs=3000)
                Logger.LogIns().logger.info("[Client] wait done")
            self.nextBlockSize = 0
            Logger.LogIns().logger.info(
                "[Client] Send to Server done. Seek device result:  " + str(seekResult))
        except Exception:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)
        finally:
            self.sendLock.release()
            return isOk

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())

    def handleDisconnect(self):
        self.serverDisconnected.emit(self.daemonStatus)

        self.daemonStatus.isDaemonStarted = False
        self.daemonStatus.deviceId = -1

        # Daemon斷訊時更新UI與tray狀態
        Logger.LogIns().logger.info("[Client] handleDisconnect daemonStatusUpdateSignal emit")
        self.daemonStatus.daemonStatusUpdateSignal.emit(self.daemonStatus)
        self.killDuplicateApp()
        self.isConnected = False
        self.isVerified = False
        self.isInitial = False
        self.processingFinder()

    def serverHasError(self):
        Logger.LogIns().logger.info("server has errer socket state: {}".format(self.tcpSocket.state()))
        Logger.LogIns().logger.info("QAbstractSocket.ConnectedState: {}".format(QAbstractSocket.ConnectedState))

        # server發生錯誤時要判斷目前的狀態，如果socket還是連著的話就不將daemon的status設為斷線
        if self.tcpSocket.state() != QAbstractSocket.ConnectedState:
            if self.daemonStatus.isDaemonStarted == True:
                self.daemonStatus.isDaemonStarted = False
                self.daemonStatus.deviceId = -1

                # Daemon斷訊時更新UI與tray狀態
                Logger.LogIns().logger.info("[Client] serverHasError daemonStatusUpdateSignal emit")
                self.daemonStatus.daemonStatusUpdateSignal.emit(self.daemonStatus)

        Logger.LogIns().logger.error("[Client] Socket error: {}".format(self.tcpSocket.errorString()))
        Logger.LogIns().logger.error("[Client] Socket error code: {}".format(self.tcpSocket.error()))
        print("Error: {}".format(self.tcpSocket.errorString()))

    def composed_content_data(self, target, data):
        data_head = "%head%"
        data_tail = "%tail%"

        target_data = target + data
        content_data = data_head + target_data + data_tail
        return content_data

    def get_command_array(self, data):
        data_array = []
        raw_data = data
        data_head = "%head%"
        data_tail = "%tail%"

        while data_head in raw_data and data_tail in raw_data:
            head_loc = raw_data.find(data_head) + len(data_head)
            tail_loc = raw_data.find(data_tail)
            command_data = raw_data[head_loc:tail_loc]
            data_array.append(command_data)

            #刪除已經取得的資料
            raw_data = raw_data[tail_loc + len(data_tail):]

        return data_array

class ConfigObj:

    def __init__(self):
        self.param = None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Checker:
    def __init__(self, client, t0, t1, t2):
        self.client = client
        self.t0 = t0
        self.t1 = t1
        self.t2 = t2
        self.isVerfing = False
        self.isFetching = False

    def tryConnect(self):
        Logger.LogIns().logger.info("[Client] Try to connect socket server")
        if not self.client.isConnected:
            Logger.LogIns().logger.info("try to connect")
            self.client.start()
        else:
            Logger.LogIns().logger.info("[Client] Connect to socket server successful")
            self.t0.stop()
            self.t1.start(1000)

    def verify(self):
        Logger.LogIns().logger.info("[Client] Try to verify with socket server")
        if not self.isVerfing:
            self.isVerfing = True
            if not self.client.isVerified:
                # verify
                vv = Verification.Verifier()
                vv.genEncode()
                isOk = self.client.queryRequest(Command.TARGET_VERIFY, vv.toJson(), isWaitReady=True)
                if isOk or self.client.isConnected:
                    Logger.LogIns().logger.info("[Client] Verify with socket server successful")
                    self.client.isVerified = True
                    self.t1.stop()
                    self.t2.start(1000)

                    # write default applocale in DB
                    locale = appLocaleData.appLocaleRecorder().appLocale
                    self.client.queryRequest(Command.TARGET_SET_LOCALE, locale)

                    # notify daemon to  write file
                    setting = loggerSetting.setting()
                    self.client.queryRequest(Command.TARGET_SET_APPDATA_PATH, setting)

    def fetchProperties(self):
        Logger.LogIns().logger.info("[Client] Try to fetch device and system properties form socket server")
        if not self.isFetching:
            self.isFetching = True
            if self.client.isVerified:
                commadList = [Command.TARGET_NOTIFICATION_EMAIL, Command.TARGET_PROPERTY,
                              Command.TARGET_CONFIG,
                              Command.TARGET_SCHEDULE, Command.TARGET_ENERGY_SETTINGS, Command.TARGET_MOBILE_LOGIN,
                              Command.TARGET_UPDATE_STATUS, Command.TARGET_UPDATE_RESULT]
                for command in commadList:
                    retry = 0
                    while retry < 3:
                        try:
                            isOk = self.client.queryRequest(command, isWaitReady=True)
                        except Exception:
                            Logger.LogIns().logger.error("[Client] Fetch device and system properties error")
                            Logger.LogIns().logger.error(traceback.print_exc())
                        if not isOk:
                            retry += 1
                        else:
                            break
                        if retry == 3:
                            break
                            # refetch
                self.t2.stop()
                Logger.LogIns().logger.info("[Client] Fetch Successful")
                self.client.isInitial = True

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    client = Client()
    timer = QTimer()
    timer.timeout.connect(client.issueRequest)
    timer.start(3000)
    sys.exit(app.exec_())
