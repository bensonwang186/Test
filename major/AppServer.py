import json
import sys
import threading
import traceback
import datetime
from PyQt5.QtCore import (pyqtSignal, QCoreApplication, QObject, QByteArray, QDataStream, QIODevice)
from PyQt5.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket)

from System import systemFunction
from Utility import Logger
from major import Command, Verification
from model_Json.tables.EmailNotification import EmailNotification
from model_Json.tables.EnergyCost import EnergyCost
from model_Json.tables.EnergyCost import EnergySetting


class STServer(QObject):
    isClientExist = False
    port = 31111
    ip = "127.0.0.1"
    tcpSockets = {}
    watch_dog_tcp_sockets = {}
    nonVerifyTcpSockets = {}
    tcpSocketsSendLock = None

    fetchEmailNotificationSignal = pyqtSignal(object)
    fetchMobileLoginSignal = pyqtSignal(object)

    setUPSAlarmSignal = pyqtSignal(object)
    setSoftSoundSignal = pyqtSignal(object)
    setRuntimeSignal = pyqtSignal(object, object)
    setVoltageSignal = pyqtSignal(object)
    setSensitivitySignal = pyqtSignal(object)
    setShutdownTypeSignal = pyqtSignal(object)
    setScheduleSignal = pyqtSignal(object)
    setNotificationSignal = pyqtSignal(object)
    setEnergySettingSignal = pyqtSignal(object)
    doSelfTestSignal = pyqtSignal()
    sendTestEmailSignal = pyqtSignal()
    setVerifySettingsSignal = pyqtSignal()
    oathExchangedSignal = pyqtSignal(object)
    setMobileSolutionSignal = pyqtSignal(object)
    setMobileLoginSignal = pyqtSignal(object)
    setLanguageSignal = pyqtSignal(object)
    showAppDisplaySignal = pyqtSignal()
    updateUPSNameSignal = pyqtSignal(object)
    eventOccurSignal = pyqtSignal(object)
    setAppDataPathSignal = pyqtSignal(object)
    shutdownAlertSignal = pyqtSignal(object)
    check_update_signal = pyqtSignal()
    update_status_signal = pyqtSignal()
    run_update_signal = pyqtSignal(object)
    run_restore_signal = pyqtSignal()
    update_result_signal = pyqtSignal()
    fetch_cloud_data_signal = pyqtSignal(object)
    cloud_verify_signal = pyqtSignal(object)
    watch_dog_software_result_signal = pyqtSignal(object)

    def __init__(self, device, parent=None):
        super(STServer, self).__init__(parent)
        Logger.LogIns().logger.info("AppServer init...")
        self.networkSession = None
        self.device = device
        self.tcpServer = QTcpServer(self)
        self.tcpSocketsSendLock = threading.Lock()
        Logger.LogIns().logger.info("AppServer: listening port...")
        if not self.tcpServer.listen(QHostAddress("0.0.0.0"), self.port):
            Logger.LogIns().logger.info("AppServer: listening port failure...")
            return
        else:
            Logger.LogIns().logger.info("AppServer: listen success")
            for ipAddress in QNetworkInterface.allAddresses():
                if ipAddress != QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                    Logger.LogIns().logger.info("QHostAddress break,,"+"ipAddress: "+str(ipAddress)+", QHostAddress.LocalHost: "+str(QHostAddress.LocalHost)+", ipAddress.toIPv4Address()"+str(ipAddress.toIPv4Address()))
                    break
            else:
                Logger.LogIns().logger.info("QHostAddress break Not break")
                ipAddress = QHostAddress(QHostAddress.LocalHost)
                Logger.LogIns().logger.info("QHostAddress listened Host: "+str(QHostAddress.LocalHost))
            self.ip = ipAddress.toString()
        try:
            self.tcpServer.newConnection.connect(self.get_tcp_socket)

        except Exception:
            Logger.LogIns().logger.info("STServer: init error!")
            Logger.LogIns().logger.info(traceback.format_exc())
            # traceback.print_exc(file=sys.stdout)

    def clientDisconnect(self, key):
        if len(self.tcpSockets.keys()) > 0 and self.tcpSockets.get(key):
            self.tcpSockets.pop(key)
            print(key)

        if len(self.watch_dog_tcp_sockets) > 0 and self.watch_dog_tcp_sockets.get(key):
            self.watch_dog_tcp_sockets.pop(key)
            print(key)

    def get_tcp_socket(self):
        Logger.LogIns().logger.info("new client connection")
        Logger.LogIns().is_client_connected = True
        try:
            clientConnection = self.tcpServer.nextPendingConnection()
            clientConnection.nextBlockSize = 0
            key = str(clientConnection.peerAddress()) + str(clientConnection.peerPort())

            self.nonVerifyTcpSockets[key] = clientConnection
            # self.tcpSockets[key] = clientConnection
            verifyCount = 0
            for k, v in self.tcpSockets.items():
                if v.ConnectedState is QTcpSocket.ConnectedState:
                    verifyCount += 1


            nonVerifyCount = 0
            for k, v in self.nonVerifyTcpSockets.items():
                if v.ConnectedState is QTcpSocket.ConnectedState:
                    nonVerifyCount += 1

            # logger.info("connected client count: " + str(verifyCount) + " at : " + str(datetime.datetime.now().time()))
            # logger.info("connected client non-count: " + str(nonVerifyCount) + " at : " + str(datetime.datetime.now().time()))
            if verifyCount >= 1 and nonVerifyCount >= 1:
                self.showAppDisplaySignal.emit()

            clientConnection.readyRead.connect(lambda: self.reqHandle(key))
            clientConnection.disconnected.connect(lambda: self.clientDisconnect(key))
        except Exception:
            print("failed")
            traceback.print_exc(file=sys.stdout)
            # self.tcpSockets[key].readyRead.connect(lambda: self.reqHandle(key))

    def connectionVerify(self, key):
        clientConnection = self.nonVerifyTcpSockets.get(key)

        if clientConnection is None:
            return

        if clientConnection.bytesAvailable() > 0:
            stream = QDataStream(clientConnection)
            stream.setVersion(QDataStream.Qt_5_0)

            byte_size = clientConnection.bytesAvailable()
            text_from_server_byte = stream.readRawData(byte_size)
            text_from_server = text_from_server_byte.decode("utf-8")
            command_array = self.get_command_array(text_from_server)

            for command in command_array:
                self.execute_verify_command(key, command)



    def reqHandle(self, key):
        Logger.LogIns().logger.info("[Server] Receive data from client Start")
        # non verify
        try:
            canVerify = len(self.nonVerifyTcpSockets.keys()) > 0 and self.nonVerifyTcpSockets.get(key) is not None
        except Exception:
            traceback.print_exc(file=sys.stdout)
        if canVerify:
            try:
                # if self.nonVerifyTcpSockets:
                print("verify")
                self.connectionVerify(key)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        else:
            try:
                # verified
                clientConnection = self.tcpSockets.get(key)

                if clientConnection is None:
                    clientConnection = self.watch_dog_tcp_sockets.get(key)

                if clientConnection.bytesAvailable() > 0:
                    stream = QDataStream(clientConnection)
                    stream.setVersion(QDataStream.Qt_5_0)

                    buffer_size = clientConnection.bytesAvailable()
                    text_from_client_byte = stream.readRawData(buffer_size)
                    text_from_client = text_from_client_byte.decode("utf-8")
                    command_array = self.get_command_array(text_from_client)

                    for command in command_array:
                        self.execute_command(command, clientConnection)

                Logger.LogIns().logger.info("[Server] Receive data from client done")
            except Exception:
                Logger.LogIns().logger.error("[Server] Receive data from client Error")
                Logger.LogIns().logger.error(traceback.print_exc())
                traceback.print_exc(file=sys.stdout)

    def execute_command(self, textFromClient, clientConnection):
        Logger.LogIns().logger.info("[Server] Receive data from client: " + str(textFromClient))
        print("textFromClient: " + str(textFromClient))

        if textFromClient == Command.TARGET_STATUS:
            # data = Command.TARGET_STATUS + self.device.deviceStatus.toJson()
            data = self.device.deviceStatus.toJson()
            print("Command.TARGET_STATUS:" + data)
            self.sendToClient(Command.TARGET_STATUS, data, clientConnection)
        if textFromClient == Command.TARGET_NOTIFICATION_EMAIL:
            self.fetchEmailNotificationSignal.emit(clientConnection)
        if textFromClient == Command.TARGET_CONFIG:
            try:
                data = self.device.dataSource.configurationSetting.toJson()
                print("Command.TARGET_CONFIG: " + data)
                self.sendToClient(Command.TARGET_CONFIG, data, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if textFromClient == Command.TARGET_PROPERTY:
            # data = Command.TARGET_PROPERTY + self.device.devicePropData.toJson()
            try:
                data = self.device.devicePropData.toJson()
            except:
                data = ""
            print("Command.TARGET_CONFIG: " + data)
            self.sendToClient(Command.TARGET_PROPERTY, data, clientConnection)
        if Command.TARGET_EVENT_LOG in textFromClient:
            try:
                # data = Command.TARGET_PROPERTY + self.device.devicePropData.toJson()
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject)
                print(jsonObject["param"])
                self.device.summaryFilter = jsonObject["param"]
                data = self.device.dataSource.queryEventLogByDuration(jsonObject["param"])
                jsonString = json.dumps(data, default=systemFunction.jsonSerialize)
                self.sendToClient(Command.TARGET_EVENT_LOG, jsonString, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if textFromClient == Command.TARGET_SCHEDULE:
            try:
                schData = self.device.dataSource.readScheduleSetting()
                data = json.dumps(schData, ensure_ascii=False, default=systemFunction.jsonSerialize)
                # data = Command.TARGET_SCHEDULE + jsonData
                print("Command.TARGET_SCHEDULE: " + data)
                self.sendToClient(Command.TARGET_SCHEDULE, data, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if textFromClient == Command.TARGET_MOBILE_LOGIN:
            try:
                self.fetchMobileLoginSignal.emit(clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if textFromClient == Command.TARGET_ENERGY_SETTINGS:
            try:
                settings = self.device.dataSource.energySetting
                data = json.dumps(settings, ensure_ascii=False, default=systemFunction.jsonSerialize)
                # data = Command.TARGET_ENERGY_SETTINGS + jsonData
                print("TARGET_ENERGY_SETTINGS: " + data)
                self.sendToClient(Command.TARGET_ENERGY_SETTINGS, data, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)
            pass
        if Command.TARGET_SET_ENERGY_SETTINGS in textFromClient:
            dataStartIndex = textFromClient.find("{")
            # target = textFromServer[:dataStartIndex]
            content = textFromClient[dataStartIndex:]
            if content:
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                print(param)
                displayDic2 = json.loads(param)
                energySetting = EnergySetting(displayDic2[0])
                energyCostList = []
                for costString in displayDic2[1]:
                    energyCostList.append(EnergyCost(costString))
                self.setEnergySettingSignal.emit((energySetting, energyCostList))
                print(energySetting)
                print(energyCostList)

        if Command.TARGET_SET_UPS_ALARM in textFromClient:
            dataStartIndex = textFromClient.find("{")
            # target = textFromServer[:dataStartIndex]
            content = textFromClient[dataStartIndex:]
            jsonObject = json.loads(content)
            print(jsonObject)
            print(jsonObject["param"])
            self.setUPSAlarmSignal.emit(jsonObject["param"])

        if Command.TARGET_SET_APPDATA_PATH in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject)
                print(jsonObject["param"])
                self.setAppDataPathSignal.emit(jsonObject["param"])
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_SOFT_SOUND in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject)
                print(jsonObject["param"])
                self.setSoftSoundSignal.emit(jsonObject["param"])
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_RUNTIME in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject)
                print(jsonObject["param"])
                params = jsonObject["param"]
                print(len(params))
                if len(params) >= 2:  # 2 is runtime setting param
                    self.setRuntimeSignal.emit(params[0], params[1])
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_TRANSFER_VOLT in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                params = jsonObject["param"]
                print(len(params))
                if len(params) >= 2:  # 2 is runtime setting param
                    self.setVoltageSignal.emit((params[0], params[1]))
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_SENSITIVITY in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                self.setSensitivitySignal.emit(param)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_SHUTDOWN_TYPE in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                self.setShutdownTypeSignal.emit(param)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_MOBILE_SOLUTION in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                self.setMobileSolutionSignal.emit(param)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_MOBILE_LOGIN in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                self.setMobileLoginSignal.emit(param)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_SCHEDULE in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                displayDic2 = json.loads(param)
                self.setScheduleSignal.emit(displayDic2)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_EMAIL in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                try:
                    jsonObject = json.loads(content)
                    param = jsonObject["param"]
                    email = EmailNotification(param)
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                self.setNotificationSignal.emit(email)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_SELF_TEST in textFromClient:
            try:
                self.doSelfTestSignal.emit()
                data = self.device.dataSource.configurationSetting.toJson()
                self.sendToClients(Command.TARGET_CONFIG, data)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_ENERGY_REPORT in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                # target = textFromServer[:dataStartIndex]
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                dateJsonObj = json.loads(param)
                startDate = systemFunction.transferStringToDatetime(dateJsonObj["startDate"])
                endDate = systemFunction.transferStringToDatetime(dateJsonObj["endDate"])
                indexTuple = self.device.dataSource.energyReportQuery(startDate, endDate)
                resp = json.dumps(indexTuple, default=systemFunction.jsonSerialize)
                Logger.LogIns().logger.info("TARGET_ENERGY_REPORT response" + str(resp))
                self.sendToClient(Command.TARGET_ENERGY_REPORT, resp, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_EVENT_LOG_PAGE in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                dateJsonObj = json.loads(param)
                startDate = systemFunction.transferStringToDatetime(dateJsonObj["startDate"])
                endDate = systemFunction.transferStringToDatetime(dateJsonObj["endDate"])
                paging = dateJsonObj["paging"]

                level = None
                if "level" in dateJsonObj.keys():
                    level = dateJsonObj["level"]

                queryStr = None
                if "queryStr" in dateJsonObj.keys():
                    queryStr = dateJsonObj["queryStr"]

                limit = 10
                if "limit" in dateJsonObj.keys():
                    limit = dateJsonObj["limit"]

                currentPageNo = 0
                limitId = 0
                if paging is True:
                    if "currentPageNo" in dateJsonObj.keys():
                        currentPageNo = dateJsonObj["currentPageNo"]

                    if "limitId" in dateJsonObj.keys():
                        limitId = dateJsonObj["limitId"]

                logs, pageIndex = self.device.dataSource.queryEventLog(startDate, endDate, level, queryStr, limit,
                                                                       paging, currentPageNo, limitId)
                jsonlogs = [item.toJson() for item in logs]
                tup = (jsonlogs, pageIndex)
                resp = json.dumps(tup)
                # resp = json.dumps([item.toJson() for item in logs])
                Logger.LogIns().logger.info("TARGET_EVENT_LOG_PAGE response" + str(resp))
                self.sendToClient(Command.TARGET_EVENT_LOG_PAGE, resp, clientConnection)
            except Exception:
                Logger.LogIns().logger.error(traceback.format_exc())

        if Command.TARGET_CLEAR_ALL_EVENTLOGS in textFromClient:
            try:
                resp = self.device.dataSource.clearEventLogs()
                Logger.LogIns().logger.info("TARGET_CLEAR_ALL_EVENTLOGS response: {0}".format(str(resp)))
                self.sendToClients(Command.TARGET_CLEAR_ALL_EVENTLOGS, resp)
            except Exception:
                Logger.LogIns().logger.error(traceback.format_exc())

        if Command.TARGET_SET_TEST_EMAIL in textFromClient:
            try:
                self.sendTestEmailSignal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_EXCHANGE_OAUTH in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]

                jsonObject = json.loads(content)
                param = jsonObject["param"]
                self.oathExchangedSignal.emit(param)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_VERIFY_EMAIL in textFromClient:
            try:
                self.setVerifySettingsSignal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)
        if Command.TARGET_SET_LOCALE in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject["param"])
                params = jsonObject["param"]
                print(params)

                self.setLanguageSignal.emit(params)

            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SET_UPS_NAME in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject["param"])
                params = jsonObject["param"]
                print(params)

                self.updateUPSNameSignal.emit(params)

            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_CHECK_UPDATE in textFromClient:
            try:
                print("App server get TARGET_CHECK_UPDATE message!!!")
                self.check_update_signal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_UPDATE_STATUS in textFromClient:
            try:
                print("App server get TARGET_UPDATE_STATUS message!!!")
                self.update_status_signal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SOFTWARE_UPDATE in textFromClient:
            try:
                print("App server get TARGET_SOFTWARE_UPDATE message!!!")
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
                jsonObject = json.loads(content)
                print(jsonObject["param"])
                params = jsonObject["param"]
                print(params)
                self.run_update_signal.emit(params)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_SOFTWARE_RESTORE in textFromClient:
            try:
                self.run_restore_signal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_UPDATE_RESULT in textFromClient:
            try:
                self.update_result_signal.emit()
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_CLOUD_DATA_DISPLAY in textFromClient:
            try:
                self.fetch_cloud_data_signal.emit(clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_CLOUD_VERIFY in textFromClient:
            try:
                self.cloud_verify_signal.emit(clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_SUCCESS in textFromClient:
            try:
                self.watch_dog_software_result_signal.emit(Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_SUCCESS)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_FAILED in textFromClient:
            try:
                self.watch_dog_software_result_signal.emit(Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_FAILED)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_SUCCESS in textFromClient:
            try:
                self.watch_dog_software_result_signal.emit(Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_SUCCESS)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_FAILED in textFromClient:
            try:
                self.watch_dog_software_result_signal.emit(Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_FAILED)
            except Exception:
                traceback.print_exc(file=sys.stdout)

    def execute_verify_command(self, key, textFromClient):
        if Command.TARGET_VERIFY in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
            except Exception:
                traceback.print_exc(file=sys.stdout)

            try:
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                print(param)
                verify = Verification.Verifier(param)
                now = datetime.datetime.now()
                for i in range(0, 5):

                    d1 = now - datetime.timedelta(seconds=i)
                    data = d1.strftime("%Y-%m-%d %H:%M:%S")

                    if verify.verify(data, verify.sha1):
                        self.tcpSockets[key] = self.nonVerifyTcpSockets.pop(key)
                        verifyRe = Verification.Verifier()
                        verifyRe.genEncode()
                        # data = Command.TARGET_VERIFY + verifyRe.toJson()
                        data = verifyRe.toJson()
                        print("Command.TARGET_VERIFY: " + data)
                        # self.sendToClient(Command.TARGET_VERIFY, data, clientConnection)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        if Command.TARGET_WATCH_DOG_VERIFY in textFromClient:
            try:
                dataStartIndex = textFromClient.find("{")
                content = textFromClient[dataStartIndex:]
            except Exception:
                traceback.print_exc(file=sys.stdout)

            try:
                jsonObject = json.loads(content)
                param = jsonObject["param"]
                print(param)
                verify = Verification.Verifier(param)
                now = datetime.datetime.now()
                for i in range(0, 5):

                    d1 = now - datetime.timedelta(seconds=i)
                    data = d1.strftime("%Y-%m-%d %H:%M:%S")

                    if verify.verify(data, verify.sha1):
                        self.watch_dog_tcp_sockets[key] = self.nonVerifyTcpSockets.pop(key)
                        verifyRe = Verification.Verifier()
                        verifyRe.genEncode()
                        data = verifyRe.toJson()
                        print("Command.TARGET_WATCH_DOG_VERIFY" + data)
                        self.send_to_watch_dog(Command.TARGET_WATCH_DOG_VERIFY, "")
            except Exception:
                traceback.print_exc(file=sys.stdout)

    def sendToClient(self, target, data, client):
        Logger.LogIns().logger.info("Send to Client, TARGET: " + str(target) + ", Data: " + str(data)+", Client: "+str(client.isValid()))
        try:
            self.tcpSocketsSendLock.acquire()

            conData = self.composed_content_data(target, data);# target + data + target  # format is target{xx : 123}target, ex: config{ "configId" : 1}config

            block = QByteArray()
            out = QDataStream(block, QIODevice.WriteOnly)
            out.setVersion(QDataStream.Qt_5_0)
            byte_content = conData.encode("utf-8")
            out.writeRawData(byte_content)
            seekResult = out.device().seek(0)
            print("send: " + conData)
            client.write(block)
            client.flush()
            Logger.LogIns().logger.info(
                "[Server] Send to Client done. Seek deivce result: "+str(seekResult))
            # client.waitForReadyRead(3000)
        except Exception:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)
        finally:
            self.tcpSocketsSendLock.release()
            # client.flush()

    # def sendToClient(self, mesg):
    def sendToClients(self, target, data):
        if target is not  Command.TARGET_STATUS:
            Logger.LogIns().logger.info("Send to Clientsss, TARGET: "+str(target)+", Data: "+str(data))
        if target is Command.TARGET_STATUS \
                or target is Command.TARGET_PROPERTY \
                or target is Command.TARGET_CONFIG \
                or target is Command.TARGET_ENERGY_REPORT \
                or target is Command.TARGET_ENERGY_SETTINGS \
                or target is Command.TARGET_SCHEDULE \
                or target is Command.TARGET_EVENT_LOG \
                or target is Command.TARGET_EVENT_LOG_PAGE\
                or target is Command.TARGET_SET_MOBILE_LOGIN\
                or target is Command.TARGET_SET_UPS_NAME:
            pass
        else:
            paramObj = ParamObj()
            paramObj.param = data
            data = paramObj.toJson()
        if self.tcpSockets and len(self.tcpSockets.keys()) > 0:
            for client in self.tcpSockets.values():
                self.sendToClient(target, data, client)

    def send_to_watch_dog(self, target, data):
        if self.watch_dog_tcp_sockets and len(self.watch_dog_tcp_sockets.keys()) > 0:
            for client in self.watch_dog_tcp_sockets.values():
                self.sendToClient(target, data, client)

    def composed_content_data(self, target, data):
        data_head = "%head%"
        data_tail = "%tail%"

        target_data = target + data + target
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

class AppServerRunner(QObject):
    def __init__(self, device, parent=None):
        super(QObject, self).__init__(parent)
        self.server = STServer(device)

    def sendToClient(self, target, data, client):
        self.server.sendToClient(target, data, client)

    def sendDataToClients(self, target, data):
        # data = target + data + target
        self.server.sendToClients(target, data)

    def sendToClients(self, data):
        self.server.sendToClients(data)

    def send_to_watch_dog(self, target, data):
        self.server.send_to_watch_dog(target, data)

    @property
    def fetchEmailNotificationSignal(self):
        return self.server.fetchEmailNotificationSignal

    @fetchEmailNotificationSignal.setter
    def fetchEmailNotificationSignal(self, value):
        self.server.fetchEmailNotificationSignal = value

    @property
    def fetchMobileLoginSignal(self):
        return self.server.fetchMobileLoginSignal

    @fetchMobileLoginSignal.setter
    def fetchMobileLoginSignal(self, value):
        self.server.fetchMobileLoginSignal = value

    @property
    def setUPSAlarmSignal(self):
        return self.server.setUPSAlarmSignal

    @setUPSAlarmSignal.setter
    def setUPSAlarmSignal(self, value):
        self.server.setUPSAlarmSignal = value

    @property
    def setSoftSoundSignal(self):
        return self.server.setSoftSoundSignal

    @setSoftSoundSignal.setter
    def setSoftSoundSignal(self, value):
        self.server.setSoftSoundSignal = value

    @property
    def setRuntimeSignal(self):
        return self.server.setRuntimeSignal

    @setRuntimeSignal.setter
    def setRuntimeSignal(self, value):
        self.server.setRuntimeSignal = value

    @property
    def setVoltageSignal(self):
        return self.server.setVoltageSignal

    @setVoltageSignal.setter
    def setVoltageSignal(self, value):
        self.server.setVoltageSignal = value

    @property
    def setSensitivitySignal(self):
        return self.server.setSensitivitySignal

    @setSensitivitySignal.setter
    def setSensitivitySignal(self, value):
        self.server.setSensitivitySignal = value

    @property
    def setShutdownTypeSignal(self):
        return self.server.setShutdownTypeSignal

    @setShutdownTypeSignal.setter
    def setShutdownTypeSignal(self, value):
        self.server.setShutdownTypeSignal = value

    @property
    def setScheduleSignal(self):
        return self.server.setScheduleSignal

    @setScheduleSignal.setter
    def setScheduleSignal(self, value):
        self.server.setScheduleSignal = value

    @property
    def setNotificationSignal(self):
        return self.server.setNotificationSignal

    @setNotificationSignal.setter
    def setNotificationSignal(self, value):
        self.server.setNotificationSignal = value

    @property
    def doSelfTestSignal(self):
        return self.server.doSelfTestSignal

    @doSelfTestSignal.setter
    def doSelfTestSignal(self, value):
        self.server.doSelfTestSignal = value

    @property
    def setEnergySettingSignal(self):
        return self.server.setEnergySettingSignal

    @setEnergySettingSignal.setter
    def setEnergySettingSignal(self, value):
        self.server.setEnergySettingSignal = value

    @property
    def sendTestEmailSignal(self):
        return self.server.sendTestEmailSignal

    @sendTestEmailSignal.setter
    def sendTestEmailSignal(self, value):
        self.server.sendTestEmailSignal = value

    @property
    def setVerifySettingsSignal(self):
        return self.server.setVerifySettingsSignal

    @setVerifySettingsSignal.setter
    def setVerifySettingsSignal(self, value):
        self.server.setVerifySettingsSignal = value

    @property
    def oathExchangedSignal(self):
        return self.server.oathExchangedSignal

    @oathExchangedSignal.setter
    def oathExchangedSignal(self, value):
        self.server.oathExchangedSignal = value

    @property
    def setLanguageSignal(self):
        return self.server.setLanguageSignal

    @setLanguageSignal.setter
    def setLanguageSignal(self, value):
        self.server.setLanguageSignal = value

    @property
    def showAppDisplaySignal(self):
        return self.server.showAppDisplaySignal

    @showAppDisplaySignal.setter
    def showAppDisplaySignal(self, value):
        self.server.showAppDisplaySignal = value

    @property
    def setMobileSolutionSignal(self):
        return self.server.setMobileSolutionSignal

    @setMobileSolutionSignal.setter
    def setMobileSolutionSignal(self, value):
        self.server.setMobileSolutionSignal = value

    @property
    def setMobileLoginSignal(self):
        return self.server.setMobileLoginSignal

    @setMobileLoginSignal.setter
    def setMobileLoginSignal(self, value):
        self.server.setMobileLoginSignal = value

    @property
    def updateUPSNameSignal(self):
        return self.server.updateUPSNameSignal

    @updateUPSNameSignal.setter
    def updateUPSNameSignal(self, value):
        self.server.updateUPSNameSignal = value

    @property
    def eventOccurSignal(self):
        return self.server.eventOccurSignal

    @eventOccurSignal.setter
    def eventOccurSignal(self, value):
        self.server.eventOccurSignal = value

    @property
    def setAppDataPathSignal(self):
        return self.server.setAppDataPathSignal

    @setAppDataPathSignal.setter
    def setAppDataPathSignal(self, value):
        self.server.setAppDataPathSignal = value

    @property
    def shutdownAlertSignal(self):
        return self.server.shutdownAlertSignal

    @shutdownAlertSignal.setter
    def shutdownAlertSignal(self, value):
        self.server.shutdownAlertSignal = value

    @property
    def check_update_signal(self):
        return self.server.check_update_signal

    @check_update_signal.setter
    def check_update_signal(self, value):
        self.server.check_update_signal = value

    @property
    def update_status_signal(self):
        return self.server.update_status_signal

    @update_status_signal.setter
    def update_status_signal(self, value):
        self.server.update_status_signal = value

    @property
    def run_update_signal(self):
        return self.server.run_update_signal

    @run_update_signal.setter
    def run_update_signal(self, value):
        self.server.run_update_signal = value

    @property
    def run_restore_signal(self):
        return self.server.run_restore_signal

    @run_restore_signal.setter
    def run_restore_signal(self, value):
        self.server.run_restore_signal = value

    @property
    def update_result_signal(self):
        return self.server.update_result_signal

    @update_result_signal.setter
    def update_result_signal(self, value):
        self.server.update_result_signal = value

    @property
    def fetch_cloud_data_signal(self):
        return self.server.fetch_cloud_data_signal

    @fetch_cloud_data_signal.setter
    def fetch_cloud_data_signal(self, value):
        self.server.fetch_cloud_data_signal = value

    @property
    def cloud_verify_signal(self):
        return self.server.cloud_verify_signal

    @cloud_verify_signal.setter
    def cloud_verify_signal(self, value):
        self.server.cloud_verify_signal = value

    @property
    def watch_dog_software_result_signal(self):
        return self.server.watch_dog_software_result_signal

    @watch_dog_software_result_signal.setter
    def watch_dog_software_result_signal(self, value):
        self.server.watch_dog_software_result_signal = value

class ParamObj:
    def __init__(self):
        self.param = None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


if __name__ == '__main__':
    # pass
    # import sys
    app = QCoreApplication(sys.argv)
    # runner = AppServerRunner()
    server = STServer(None)
    # timer = QTimer()
    # timer.timeout.connect(server.sendToClient2)
    # timer.start(3000)
    # TimerRepearter.TimerRepearter(3.0, server.sendToClient).start()

    # dialog.show()
    sys.exit(app.exec_())
