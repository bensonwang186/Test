import os
import datetime
import traceback
import json
import ssl
import sys
from pyfcm import FCMNotification
import time
import functools
import paho.mqtt.client as mqtt
from PyQt5.QtCore import QTimer, QObject
from System import ValueId
from System import systemDefine as sysDef
from Utility import DataCryptor, Logger, Scheduler
from model_Json import DevicePushMessageData
from Events import Event, EventsMobile
from views.Custom.CountryTableData import CountryTable
from System import settings

AFTER_EVENT_MAXIMUM = 600 # 一次3秒，600次 = 30分鐘
class FcmMsgProvider:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
        return class_._instance

    def __init__(self, device):
        self.device = device
        self.apikey = None
        self.CountryTable = CountryTable().displayData

        # PPP mobile solution"
        account = device.dataSource.readAppAccount()
        if account is not None and account.fcmApiKey is not None:
            cryptor = DataCryptor.Cryptor()
            self.apikey = cryptor.decToString(account.fcmApiKey)

    def doSendApnsSilenceMsg(self):
        try:
            Logger.LogIns().logger.info("***into doSendApnsSilenceMsg***")

            # satisfy conditions:  mobile solution enable, login success and find API key.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                    and self.device.topicId is not None and self.apikey is not None:

                sendApnsMsgFlag = False  # True: send APNS status message

                Logger.LogIns().logger.info("***msg sn chk1: " + str(self.device.devicePushSilenceMsg.SN) + "***")

                if self.device.deviceId != -1 and self.device.isLostCommunication == False:  # if UPS plugged
                    self.setDeviceConfigToSilenceMsg()
                    msg = self.device.devicePushSilenceMsg
                    sendApnsMsgFlag = True
                else:  # if communication lost
                    msg = DevicePushMessageData.SilenceMessage()
                    msg.SN = self.device.upsSN_Temp
                    msg.upsState = sysDef.UPS_StateMobile.Unable_to_establish_communication_with_UPS.value

                    Logger.LogIns().logger.info("***msg sn chk2: " + str(msg.SN) + "***")
                    # Lost Communication時, 送APNS msg次數(count)由duration / interval決定, ex:60(sec)/15(sec)= 4(times)
                    Logger.LogIns().logger.info(
                        "APNsLostCommunicationMsgTimesLimit: " + str(self.device.APNsLostCommunicationMsgTimesLimit))
                    Logger.LogIns().logger.info("APNsLostCommunicationMsgCount: " + str(self.device.APNsLostCommunicationMsgCount))

                    if self.device.APNsLostCommunicationMsgCount < self.device.APNsLostCommunicationMsgTimesLimit:
                        sendApnsMsgFlag = True

                        Logger.LogIns().logger.info("***APNS Status Msg LostCommunication Count: " + str(
                            self.device.APNsLostCommunicationMsgCount) + "***")

                        self.device.APNsLostCommunicationMsgCount += 1

                Logger.LogIns().logger.info("***Send APNS Status Msg Flag: " + str(sendApnsMsgFlag) + "***")

                if sendApnsMsgFlag == True:

                    Logger.LogIns().logger.info("***msg sn chk3: " + str(msg.SN) + "***")

                    ts = time.time()
                    msg.tstamp = int(ts)

                    jsonMsg = msg.toJson()

                    push_service = FCMNotification(api_key=self.apikey)
                    result = push_service.notify_topic_subscribers(topic_name=self.device.topicId,
                                                                   delay_while_idle=True,
                                                                   time_to_live=0,
                                                                   data_message={"title": jsonMsg},
                                                                   content_available=True,
                                                                   extra_kwargs={"subtitle": ""})

                    # To process background notifications in iOS 10, set content_available

                    Logger.LogIns().logger.info("apns msg: " + jsonMsg)
                    Logger.LogIns().logger.info("json length: " + str(len(jsonMsg)))

                    if result["success"] == 1:
                        Logger.LogIns().logger.info("***do send silence message to APNs successful.***")

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def doSendApnsAlertMsg(self):
        try:
            # satisfy conditions:  mobile solution enable, login success and find API key.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                    and self.device.topicId is not None and self.apikey is not None:

                title = self.device.devicePushAlertMsg.messageTitle
                body = self.device.devicePushAlertMsg.messageBody

                sn = ""
                if self.device.deviceId != -1 and self.device.isLostCommunication == False:  # if UPS plugged
                    sn = self.device.devicePushSilenceMsg.SN
                else:  # if communication lost
                    sn = self.device.upsSN_Temp

                push_service = FCMNotification(api_key=self.apikey)
                result = push_service.notify_topic_subscribers(topic_name=self.device.topicId, message_title=title,
                                                               body_loc_key=body, data_message={"sn": sn})
                if result["success"] == 1:
                    Logger.LogIns().logger.info("***do send alert message to APNs successful.***")

        except Exception as e:
            Logger.LogIns().logger.info(traceback.format_exc())

    def setDeviceConfigToSilenceMsg(self):

        dataSrc = self.device.dataSource
        now = datetime.datetime.now()

        config = dataSrc.readActiveConfig()
        if config is not None:
            self.device.devicePushSilenceMsg.upsName = self.device.devicePropData.modelName.value

        energySetting = dataSrc.readEnergySetting()
        cumulativeCostStrToday = ''
        cumulativeCostStrAll = ''

        # ***能耗相關設定***
        if energySetting is not None:
            if energySetting[0] is not None:
                cumulativeCostStrToday = self.CountryTable[energySetting[0].country].currency
                cumulativeCostStrAll = self.CountryTable[energySetting[0].country].currency

                self.device.devicePushSilenceMsg.countrySelection = energySetting[0].country
                self.device.devicePushSilenceMsg.unit = energySetting[0].measurement

                if energySetting[0].measurement == 0:
                    self.device.devicePushSilenceMsg.co2Emitted = energySetting[0].co2EmittedKg
                else:
                    self.device.devicePushSilenceMsg.co2Emitted = energySetting[0].co2EmittedLb

            if energySetting[1] is not None and len(energySetting[1]) > 0:
                self.device.devicePushSilenceMsg.energyCost = energySetting[1][(len(energySetting[1]) - 1)].cost
                startDateAll = energySetting[1][0].startTime

        energyStatistic = list()

        # ***當日(today)能耗資料***
        today_statistic = dataSrc.energyReportQuery(now, now)

        if today_statistic is not None:
            obj1 = DevicePushMessageData.EnergyReportStatistic()
            obj1.averageConsumption = today_statistic[0]
            obj1.cumulativeConsumption = today_statistic[0]

            cumulativeCostStrToday = cumulativeCostStrToday.replace("0.00", str(today_statistic[1]))
            obj1.cost = cumulativeCostStrToday
            obj1.co2 = today_statistic[2]
            energyStatistic.append(obj1)

        # ***累計(all)能耗資料***
        all_statistic = dataSrc.energyReportQuery(startDateAll, now)

        if all_statistic is not None:
            days = (now.date() - startDateAll.date()).days + 1
            if days <= 0:
                days = 1

            obj2 = DevicePushMessageData.EnergyReportStatistic()
            obj2.averageConsumption = round((all_statistic[0] / days), 2)
            obj2.cumulativeConsumption = all_statistic[0]

            cumulativeCostStrAll = cumulativeCostStrAll.replace("0.00", str(all_statistic[1]))
            obj2.cost = cumulativeCostStrAll
            obj2.co2 = all_statistic[2]
            energyStatistic.append(obj2)

        powerProblem = list()

        weeksEvent_1 = self.sumProblemSummary(1)
        weeksEvent_4 = self.sumProblemSummary(4)
        weeksEvent_12 = self.sumProblemSummary(12)
        weeksEvent_24 = self.sumProblemSummary(24)
        powerProblem.append(weeksEvent_1)
        powerProblem.append(weeksEvent_4)
        powerProblem.append(weeksEvent_12)
        powerProblem.append(weeksEvent_24)

        self.device.devicePushSilenceMsg.statistic = energyStatistic
        self.device.devicePushSilenceMsg.powerProblem = powerProblem

    def sumProblemSummary(self, weeks):

        logs = self.device.dataSource.queryEventLogByDuration(weeks)
        weekObj = DevicePushMessageData.powerProblemSummary()
        EventID = Event.EventID

        if logs is not None and len(logs) > 0:
            for item in logs[0]:
                if item[0] == str(EventID.ID_UTILITY_FAILURE.value):
                    weekObj.powerOutageTimes = item[1]
                    weekObj.powerOutageAmount = item[2]

                if item[0] == str(EventID.ID_UTILITY_TRANSFER_LOW.value):
                    weekObj.underVoltageTimes = item[1]
                    weekObj.underVoltageAmount = item[2]

                if item[0] == str(EventID.ID_UTILITY_TRANSFER_HIGH.value):
                    weekObj.overVoltageTimes = item[1]
                    weekObj.overVoltageAmount = item[2]

                if item[0] == str(EventID.ID_AVR_BOOST_ACTIVE.value):
                    weekObj.boostTimes = item[1]
                    weekObj.boostAmount = item[2]

                if item[0] == str(EventID.ID_AVR_BUCK_ACTIVE.value):
                    weekObj.buckTimes = item[1]
                    weekObj.buckAmount = item[2]

        return weekObj

    def sendApnsDeactivateMsg(self):
        msg = DevicePushMessageData.SilenceMessage()

        if self.device.mobileSolutionEnable is False:
            if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                if self.device.isNoneSN:
                    msg.SN = self.device.altSN
                else:
                    msg.SN = self.device.devicePropData.serialNumber.value

                msg.upsState = sysDef.UPS_StateMobile.Deactivate_PPP_mobile_solution.value
            else:  # if communication lost
                pass

        ts = time.time()
        msg.tstamp = int(ts)

        jsonMsg = msg.toJson()
        push_service = FCMNotification(api_key=self.apikey)
        result = push_service.notify_topic_subscribers(topic_name=self.device.topicId,
                                                       delay_while_idle=True,
                                                       time_to_live=0,
                                                       data_message={"title": jsonMsg},
                                                       content_available=True,
                                                       extra_kwargs={"subtitle": ""})

        if result["success"] == 1:
            Logger.LogIns().logger.info("***do send Apns deactivate msg successful.***")


class EmqMsgProvider(QObject):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
        return class_._instance

    def __init__(self, device):
        super(EmqMsgProvider, self).__init__()
        self.device = device
        self.CloudEventID = device.cloudEventId
        self.FcmMsgProvider = FcmMsgProvider(self.device)

        self.emqConnectedFlag = False
        self.mobileAppActiveFlag = False
        self.isMobileAppActiveFlagUpdate = False
        self.sendSilenceMsgCount = sysDef.APNS_SILENCE_MESSAGE_SEND_TIMES

        self.sendStatusMsgTimer = None # mobile APP inactive -> adjusted timer frequency
        self.after_event_timer = None  # 當事件發生後，會持續送ups status給emq一段時間，這個會暫停原本的send emq的timer
        self.sendSilenceMsgTimer = None # mobile APP active -> adjusted timer frequency
        self.emqAcc = None
        self.emqSecret = None
        self.EventMoble = EventsMobile.EventCloud(device)
        self.schedulerManager = self.device.schedulerManager
        self.after_event_counter = 0

        account = device.dataSource.readAppAccount()
        if account is not None and account.emqAcc is not None and account.emqSecret is not None:
            cryptor = DataCryptor.Cryptor()
            self.emqAcc = cryptor.decToString(account.emqAcc)
            self.emqSecret = cryptor.decToString(account.emqSecret)

        self.client = None
        self.pubMid = None
        self.pubSuccessFlag = False
        self.adjStatusMsgTimer = False
        self.adjSilenceMsgTimer = False
        self.btestActiveFlag = False
        self.btestDtime = None  # battery test delay time
        self.isBatteryTestFlagUpdate = False

        # send status after event occur
        self.after_event_send_counter = 0

    def createClientInstance(self):
        client = mqtt.Client()

        # software communicate with EMQ production server by TLS protocol
        # if sysDef.BUILD_FOR is sysDef.BuildConfiguration.Production.value:
        my_ca_cert = os.path.join(settings.PROJECT_ROOT_PATH, "rootCA.crt")
        my_pri_cert = os.path.join(settings.PROJECT_ROOT_PATH, "d1.crt")
        my_key_cert = os.path.join(settings.PROJECT_ROOT_PATH, "d1.key")

        ssl.match_hostname = lambda cert, hostname: True
        client.tls_set(ca_certs=my_ca_cert, certfile=my_pri_cert, keyfile=my_key_cert,
                       tls_version=ssl.PROTOCOL_TLSv1_2,
                       ciphers=None)

        client.username_pw_set(self.emqAcc, self.emqSecret)

        # Callbacks are dependent on the client loop as without the loop the callbacks aren’t triggered.
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        client.on_subscribe = self.on_subscribe
        client.on_unsubscribe = self.on_unsubscribe
        client.on_message = self.on_message
        client.on_log = self.on_log

        return client

    # Event Connection acknowledged Triggers the on_connect callback
    def on_connect(self, client, userdata, flags, rc):
        # Connection Return Codes:
        # 0: Connection successful
        # 1: Connection refused – incorrect protocol version
        # 2: Connection refused – invalid client identifier
        # 3: Connection refused – server unavailable
        # 4: Connection refused – bad username or password
        # 5: Connection refused – not authorised
        # 6 - 255: Currently unused.
        if rc == 0:
            self.emqConnectedFlag = True
            Logger.LogIns().logger.info("***on_connect callback: EMQ server connected.***")
        else:
            self.emqConnectedFlag = False
            Logger.LogIns().logger.info("***on_connect callback EMQ server connect failed with rc code= " + str(rc) + ".***")

    # Event Disconnection acknowledged Triggers the on_disconnect callback
    def on_disconnect(self, client, userdata, rc):
        # Return Code (rc)- Indication of disconnect reason. 0 is normal all other values indicate abnormal disconnection
        if rc == 0:
            self.emqConnectedFlag = False
            Logger.LogIns().logger.info("***on_disconnect callback: EMQ server disconnected.***")
        else:
            Logger.LogIns().logger.info(
                "***on_disconnect callback: EMQ server disconnect failed with rc code= " + str(rc) + ".***")

    # Event Subscription acknowledged Triggers the  on_subscribe callback
    def on_subscribe(self, client, userdata, mid, granted_qos):
        Logger.LogIns().logger.info("***on_subscribe callback mid: " + str(mid) + "***")

    # Event Un-subscription acknowledged Triggers the  on_unsubscribe callback
    def on_unsubscribe(self, client, userdata, mid):
        Logger.LogIns().logger.info("***on_unsubscribe callback mid: " + str(mid) + "***")

    # Event Publish acknowledged Triggers the on_publish callback
    def on_publish(self, client, userdata, mid):
        Logger.LogIns().logger.info("***on_publish callback mid: " + str(mid) + "***")

        # if mid == self.pubMid:
        #     self.pubSuccessFlag = True

    # Event Message Received Triggers the on_message callback
    def on_message(self, client, userdata, msg):
        # Logger.LogIns().logger.info("***on_message callback msg topic: " + str(msg.topic) + "***")

        try:
            jsonStr = msg.payload.decode("utf-8")
            Logger.LogIns().logger.info("***on_message callback msg payload: " + str(jsonStr) + "***")

            msg = json.loads(jsonStr)

            if "active" in msg:
                self.mobileAppActiveFlag = msg["active"]

                if "dur" in msg:
                    if self.mobileAppActiveFlag:  # change APNs timer frequency
                        if self.device.freqAppAct > 0 and str(self.device.freqAppAct) != str(msg["dur"]):
                            self.device.freqAppAct = int(msg["dur"])
                            if self.sendSilenceMsgTimer is not None:
                                self.adjSilenceMsgTimer = True
                        else:
                            self.adjSilenceMsgTimer = False

                    else:  # change EMQ timer frequency
                        if self.device.freqConstant > 0 and str(self.device.freqConstant) != str(msg["dur"]):
                            self.device.freqConstant = int(msg["dur"])
                            if self.sendStatusMsgTimer is not None:
                                self.adjStatusMsgTimer = True
                        else:
                            self.adjStatusMsgTimer = False

                self.isMobileAppActiveFlagUpdate = True

            if "b_test" in msg and msg["b_test"] == 0:

                check = False
                if "usn" in msg: # check UPS SN
                    if self.device.isNoneSN:
                        if msg["usn"] == self.device.altSN:
                            check = True
                    else:
                        if msg["usn"] == self.device.devicePropData.serialNumber.value:
                            check = True

                if check is True:

                    Logger.LogIns().logger.info("***on_message callback btestTs #1: " + str(self.device.btestTs) + "***")
                    Logger.LogIns().logger.info("***on_message callback btestActiveFlag #1: " + str(self.btestActiveFlag) + "***")
                    Logger.LogIns().logger.info("***on_message callback btestDtime #1: " + str(self.btestDtime) + "***")

                    if "ts" in msg and isinstance(msg["ts"],int) and msg["ts"] != self.device.btestTs: # check packet UNIX epoch time
                        self.device.btestTs = msg["ts"]  # update check timestamp
                        self.btestActiveFlag = True

                        if "dtime" in msg and isinstance(msg["dtime"],int): # dtime為Battery test延遲執行時間, 單位秒, 若不給or給0, 代表battery test立即執行
                            self.btestDtime = msg["dtime"]
                        else:
                            self.btestDtime = 0

                        self.device.cloudBtestResult = DevicePushMessageData.BatteryTestResult()

                        if "from" in msg and isinstance(msg["from"], int):
                            self.device.cloudBtestResult.BatTFrom = msg["from"]

                    self.isBatteryTestFlagUpdate = True

                Logger.LogIns().logger.info("***on_message callback btestTs #2: " + str(self.device.btestTs) + "***")
                Logger.LogIns().logger.info("***on_message callback btestActiveFlag #2: " + str(self.btestActiveFlag) + "***")
                Logger.LogIns().logger.info("***on_message callback btestDtime #2: " + str(self.btestDtime) + "***")

        except Exception:
            self.isMobileAppActiveFlagUpdate = False
            self.isBatteryTestFlagUpdate = False
            Logger.LogIns().logger.error(traceback.format_exc())

        if self.mobileAppActiveFlag is True and self.isMobileAppActiveFlagUpdate is True:
            # self.sendSilenceMsgCount = sysDef.APNS_SILENCE_MESSAGE_SEND_TIMES
            if "times" in msg:
                self.sendSilenceMsgCount = int(msg["times"])
            else:
                self.sendSilenceMsgCount = sysDef.APNS_SILENCE_MESSAGE_SEND_TIMES

    # Event Log information available Triggers the on_log callback
    def on_log(self, client, userdata, level, buf):
        Logger.LogIns().logger.info("***on_log: " + str(buf) + "***")

    def doPublish(self, jsonMsg):
        # pubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/pub"
        if self.device.isNoneSN:
            pubTopic = "c/ppp-" + self.device.altSN + "/pub"
        else:
            pubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/pub"

        Logger.LogIns().logger.info("***[doPublish]isNoneSN: " + str(self.device.isNoneSN) + "***")

        pub_result = self.client.publish(topic=pubTopic, payload=jsonMsg, qos=0, retain=False)

        Logger.LogIns().logger.info("***pub topic: " + str(pubTopic) + "***")
        Logger.LogIns().logger.info("***publish result: " + str(pub_result) + "***")

        # if pub_result[0] == 0:
        #     self.pubMid = pub_result[1]

    def clearRetainMessage(self, command):
        # pubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/pub"

        topicTail = "/sub"
        if command == "btest":
            topicTail = "/btest_sub"

        if self.device.isNoneSN:
            pubTopic = "c/ppp-" + self.device.altSN + topicTail
        else:
            pubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + topicTail

        Logger.LogIns().logger.info("***[clearRetainMessage]isNoneSN: " + str(self.device.isNoneSN) + "***")

        pub_result = self.client.publish(topic=pubTopic, payload="{}", qos=0, retain=True)

        Logger.LogIns().logger.info("***[clearRetainMessage] pub topic: " + str(pubTopic) + "***")
        Logger.LogIns().logger.info("***[clearRetainMessage] publish result: " + str(pub_result) + "***")

    def doSubcribe(self, subTopic, btestSubTopic):

        # subscribe mq message, 執行完呼叫subscribe後會在on_message這個callback function收資料
        if subTopic is not None:
            sub_result = self.client.subscribe(subTopic)

            Logger.LogIns().logger.info("***sub topic: " + str(subTopic) + "***")
            Logger.LogIns().logger.info("***subscribe result: " + str(sub_result) + "***")

        if btestSubTopic is not None:
            btest_sub_result = self.client.subscribe(btestSubTopic)

            Logger.LogIns().logger.info("***btest sub topic: " + str(btestSubTopic) + "***")
            Logger.LogIns().logger.info("***btest subscribe result: " + str(btest_sub_result) + "***")

        cnt = 10  # wait x seconds for message receive.
        while cnt > 0:
            Logger.LogIns().logger.info("***Wait for " + str(abs(cnt - 10)) + " seconds for message receive.***")
            Logger.LogIns().logger.info("***Mobile App Active Flag: " + str(self.mobileAppActiveFlag) + "***")

            newInterval = 0
            if self.mobileAppActiveFlag is True:
                if self.device.freqAppAct > 0:
                    newInterval = self.device.freqAppAct * 1000
            else:
                if self.device.freqConstant > 0:
                    newInterval = self.device.freqConstant * 1000

            if self.sendStatusMsgTimer is not None:
                preInterval = self.sendStatusMsgTimer.interval() # unit: msc
                if newInterval > 0 and preInterval != newInterval:
                    Logger.LogIns().logger.info("***change freq.: {0} -> {1} msecs ***".format(str(preInterval), str(newInterval)))
                    self.sendStatusMsgTimer.setInterval(newInterval)
                    break

            if btestSubTopic is not None:

                Logger.LogIns().logger.info("***btest btestActiveFlag: " + str(self.btestActiveFlag) + "***")
                Logger.LogIns().logger.info("***btest btestDtime: " + str(self.btestDtime) + "***")
                if self.btestActiveFlag is True and self.btestDtime is not None:

                    # new thread
                    self.schedulerManager.addBatteryTestSchedule(Scheduler.BatteryTestThread("BatteryTestThread", self.btestDtime, self))
                    self.schedulerManager.startBatteryTestSchedule()

                    # clear flag and delay time
                    self.btestActiveFlag = False
                    self.btestDtime = None
                    break

            time.sleep(1)
            cnt = cnt - 1

    def doStopLoop(self):
        # time.sleep(4)
        time.sleep(1)
        self.client.loop_stop()

    def getStatusMsg(self):
        Logger.LogIns().logger.info("***into getStatusMsg***")

        if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
            if self.device.isNoneSN:
                self.device.devicePushSilenceMsg.SN = self.device.altSN
            else:
                self.device.devicePushSilenceMsg.SN = self.device.devicePropData.serialNumber.value

            Logger.LogIns().logger.info("***msg sn" + str(self.device.devicePushSilenceMsg.SN) + "***")

            msg = self.device.devicePushSilenceMsg
        else:  # if communication lost
            msg = DevicePushMessageData.SilenceMessage()
            msg.SN = self.device.upsSN_Temp
            msg.upsState = sysDef.UPS_StateMobile.Unable_to_establish_communication_with_UPS.value
            # msg.Event = self.EventMoble.GetEventObj(EventID.ID_COMMUNICATION_LOST.name)
            self.device.cloudEvents.append(self.CloudEventID.ID_COMMUNICATION_LOST.value)
            Logger.LogIns().logger.info("***getStatusMsg ID_COMMUNICATION_LOST***")
            msg.Event = self.EventMoble.GetEventObj(self.device.cloudEvents)

            Logger.LogIns().logger.info("***msg sn: " + str(msg.SN) + "***")

        return msg

    def stop_after_event_timer(self):
        try:
            if self.after_event_timer is not None and self.after_event_timer.isActive():
                self.after_event_timer.stop()
                Logger.LogIns().logger.info("***stoped after event timer***")
        except Exception:
            Logger.LogIns().logger.info("stop after event timer failed. {}".format(traceback.format_exc()))


    # 事件觸發後每n秒發送UPS Status給mq server
    # 只會有一個timer做這件事，所以每次呼叫都要先停掉舊的timer
    def restart_send_status_after_event(self):
        Logger.LogIns().logger.info("***restart_send_status_after_event***")
        self.after_event_send_counter = 0
        try:
            self.stop_after_event_timer()
            self.after_event_timer = QTimer(self)
            self.after_event_timer.setSingleShot(False)
            self.after_event_timer.timeout.connect(functools.partial(self.send_status))
            self.after_event_timer.start(3*1000)
        except Exception:
            Logger.LogIns().logger.info("send status after event failed. {}".format(traceback.format_exc()))

    def emq_connect(self):
        if self.emqConnectedFlag:
            return True
        self.client = self.createClientInstance()

        # do connect before start loop would be better.
        self.client.connect(sysDef.EMQ_HOST, sysDef.EMQ_PORT, 60)
        self.client.loop_start()  # loop_start() will re-connections automatically in the background every 3 to 6 seconds.

        con_cnt = 30  # wait x seconds for re-connections.
        while con_cnt > 0:  # wait in loop
            Logger.LogIns().logger.info("***In wait connection loop at " + str(abs(con_cnt - 30)) + " sec.***")
            if self.emqConnectedFlag is True:
                return True
            time.sleep(1)
            con_cnt = con_cnt - 1
        return False

    def emq_disconnect(self):
        Logger.LogIns().logger.info(
            "***Check emq connected flag(before disconnect): " + str(self.emqConnectedFlag) + "***")
        self.client.disconnect()
        self.doStopLoop()
        Logger.LogIns().logger.info("***do send Status data end.***")

    def send_status(self):
        Logger.LogIns().logger.info("*** send_status***")
        sendEmqMsgFlag = False  # True: send EMQ status message
        currentMsg = None
        try:
            # satisfy conditions:  mobile solution enable, login success.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                    and self.device.topicId is not None:

                if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                    sendEmqMsgFlag = True
                else:  # if communication lost
                    Logger.LogIns().logger.info(
                        "send_status: local communication lost")
                    self.after_event_counter = 0
                    self.after_event_timer.stop()

                currentMsg = self.getStatusMsg()
                jsonMsg = currentMsg.toJson()

                Logger.LogIns().logger.info("***emq slience msg: {0}***".format(jsonMsg))
                Logger.LogIns().logger.info("***do send Status data start.***")
                Logger.LogIns().logger.info("***Check emq connected flag(init): " + str(self.emqConnectedFlag) + "***")

                if not self.emqConnectedFlag:
                    self.emq_connect()
                if self.emqConnectedFlag:  # connect success
                    Logger.LogIns().logger.info("***Need pub emq msg flag: " + str(sendEmqMsgFlag) + "***")
                    Logger.LogIns().logger.info(
                        "***Check emq connected flag(before pub): " + str(self.emqConnectedFlag) + "***")

                    if sendEmqMsgFlag is True:
                        Logger.LogIns().logger.info(
                            "***Mobile App Active Flag: " + str(self.mobileAppActiveFlag) + "***")
                        if self.mobileAppActiveFlag:
                            Logger.LogIns().logger.info(
                                "***SEND APP-ACTIVE EMQ COUNT: #" + str(self.sendSilenceMsgCount) + "***")
                            if self.sendSilenceMsgCount > 0:
                                self.doPublish(jsonMsg)
                                self.sendSilenceMsgCount -= 1
                        else:
                            self.doPublish(jsonMsg)

            self.after_event_counter += 1
            if self.after_event_counter >= AFTER_EVENT_MAXIMUM:
                self.after_event_counter = 0
                self.after_event_timer.stop()
                self.emq_disconnect()

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
            self.doStopLoop()

            if sendEmqMsgFlag is True:
                Logger.LogIns().logger.info("***emq error catched do resend.***")
                time.sleep(5)
                self.resendEmqStatusMsg(currentMsg)


    def sendEmqStatusMsg(self, init_flag):
        try:
            Logger.LogIns().logger.info("*** into sendEmqStatusMsg***")
            if init_flag is True:
                self.device.cloudEvents.append(self.CloudEventID.ID_COMMUNICATION_ESTABLISHED.value) # reset UPS status to normal
                self.doSendEmqStatusMsg()

            if self.sendStatusMsgTimer is None:
                self.sendStatusMsgTimer = QTimer(self)
                self.sendStatusMsgTimer.setSingleShot(False)
                self.sendStatusMsgTimer.timeout.connect(functools.partial(self.doSendEmqStatusMsg))

                Logger.LogIns().logger.info("***freqConstant: " + str(self.device.freqConstant) + "***")
                if self.device.freqConstant > 0:
                    Logger.LogIns().logger.info("***START SEND EMQ STATUS MSG TIMER***")
                    self.sendStatusMsgTimer.start(self.device.freqConstant * 1000)  # unit: ms
            else:
                Logger.LogIns().logger.info("***sendStatusMsgTimer is already existed***")
        except Exception:
            Logger.LogIns().logger.info(traceback.format_exc())

    def stopSendEmqStatusMsgTimer(self):
        try:
            if self.sendStatusMsgTimer is not None:
                Logger.LogIns().logger.info("***STOP SEND EMQ STATUS MSG TIMER***")
                self.sendStatusMsgTimer.stop()
                self.sendStatusMsgTimer = None
        except Exception:
            Logger.LogIns().logger.info(traceback.format_exc())

    def doSendEmqStatusMsg(self):
        sendEmqMsgFlag = False  # True: send EMQ status message
        # self.pubMid = None
        # self.pubSuccessFlag = False
        Logger.LogIns().logger.info("***into doSendEmqStatusMsg***")
        currentMsg = None
        try:
            # satisfy conditions:  mobile solution enable, login success.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                    and self.device.topicId is not None:

                if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                    sendEmqMsgFlag = True
                else:  # if communication lost
                    Logger.LogIns().logger.info(
                        "EmqLostCommunicationMsgTimesLimit: " + str(self.device.EmqLostCommunicationMsgTimesLimit))
                    Logger.LogIns().logger.info("EmqLostCommunicationMsgCount: " + str(self.device.EmqLostCommunicationMsgCount))

                    # Lost Communication時, 送emq msg次數(count)由duration / interval決定, ex:60(sec)/15(sec)= 4(times)
                    if self.device.EmqLostCommunicationMsgCount < self.device.EmqLostCommunicationMsgTimesLimit:
                        sendEmqMsgFlag = True
                        Logger.LogIns().logger.info("***EMQ Status Msg LostCommunication Count: " + str(
                            self.device.EmqLostCommunicationMsgCount) + "***")
                        self.device.EmqLostCommunicationMsgCount += 1

                currentMsg = self.getStatusMsg()
                jsonMsg = currentMsg.toJson()

                Logger.LogIns().logger.info("***emq slience msg: {0}***".format(jsonMsg))
                Logger.LogIns().logger.info("***do send Status data start.***")
                Logger.LogIns().logger.info("***Check emq connected flag(init): " + str(self.emqConnectedFlag) + "***")
                self.emqConnectedFlag = False
                self.client = self.createClientInstance()

                # do connect before start loop would be better.
                self.client.connect(sysDef.EMQ_HOST, sysDef.EMQ_PORT, 60)
                self.client.loop_start()  # loop_start() will re-connections automatically in the background every 3 to 6 seconds.

                con_cnt = 30  # wait x seconds for re-connections.
                while con_cnt > 0:  # wait in loop
                    Logger.LogIns().logger.info("***In wait connection loop at " + str(abs(con_cnt - 30)) + " sec.***")
                    if self.emqConnectedFlag is True:
                        break
                    time.sleep(1)
                    con_cnt = con_cnt - 1

                if self.emqConnectedFlag:  # connect success
                    Logger.LogIns().logger.info("***Need pub emq msg flag: " + str(sendEmqMsgFlag) + "***")
                    Logger.LogIns().logger.info("***Check emq connected flag(before pub): " + str(self.emqConnectedFlag) + "***")

                    if sendEmqMsgFlag is True:
                        Logger.LogIns().logger.info("***Mobile App Active Flag: " + str(self.mobileAppActiveFlag) + "***")
                        if self.mobileAppActiveFlag:
                            Logger.LogIns().logger.info("***SEND APP-ACTIVE EMQ COUNT: #" + str(self.sendSilenceMsgCount) + "***")
                            if self.sendSilenceMsgCount > 0:
                                self.doPublish(jsonMsg)
                                self.sendSilenceMsgCount -= 1
                        else:
                            self.doPublish(jsonMsg)


                    # subTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/sub"

                    if self.device.isNoneSN:
                        subTopic = "c/ppp-" + self.device.altSN + "/sub"
                        btestSubTopic = "c/ppp-" + self.device.altSN + "/btest_sub"
                    else:
                        subTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/sub"
                        btestSubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/btest_sub"

                    Logger.LogIns().logger.info("***isNoneSN: " + str(self.device.isNoneSN) + "***")
                    Logger.LogIns().logger.info("***subTopic: " + str(subTopic) + "***")

                    self.doSubcribe(subTopic, btestSubTopic)
                    self.client.unsubscribe(subTopic)
                    self.client.unsubscribe(btestSubTopic)

                    Logger.LogIns().logger.info("***Mobile App Active Flag: " + str(self.mobileAppActiveFlag) + "***")
                    Logger.LogIns().logger.info("***isMobileAppActiveFlagUpdate Flag: " + str(self.isMobileAppActiveFlagUpdate) + "***")

                    # clear server active flag
                    if self.isMobileAppActiveFlagUpdate is True:
                        self.clearRetainMessage("")
                        self.isMobileAppActiveFlagUpdate = False

                    # clear server active flag
                    if self.isBatteryTestFlagUpdate is True:
                        self.clearRetainMessage("btest")
                        self.isBatteryTestFlagUpdate = False

                    Logger.LogIns().logger.info("***Check emq connected flag(before disconnect): " + str(self.emqConnectedFlag) + "***")
                    self.client.disconnect()
                    self.doStopLoop()
                    Logger.LogIns().logger.info("***do send Status data end.***")

                else:
                    self.client.disconnect()
                    self.doStopLoop()

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
            self.doStopLoop()

            if sendEmqMsgFlag is True:
                Logger.LogIns().logger.info("***emq error catched do resend.***")
                time.sleep(5)
                self.resendEmqStatusMsg(currentMsg)

    def resendEmqStatusMsg(self, currentMsg):
        try:
            # self.pubMid = None
            # self.pubSuccessFlag = False

            if currentMsg is None:
                jsonMsg = self.getStatusMsg().toJson()
            else:
                jsonMsg = currentMsg.toJson()

            Logger.LogIns().logger.info("***emq slience msg: {0}***".format(jsonMsg))

            self.client = self.createClientInstance()  # new client

            # do connect before start loop would be better.
            self.client.connect(sysDef.EMQ_HOST, sysDef.EMQ_PORT, 60)
            self.client.loop_start()  # loop_start() will re-connections automatically in the background every 3 to 6 seconds.

            con_cnt = 30  # wait x seconds for re-connections.
            while con_cnt > 0:  # wait in loop
                Logger.LogIns().logger.info("***In wait connection loop at " + str(abs(con_cnt - 30)) + " sec.***")
                if self.emqConnectedFlag is True:
                    break
                time.sleep(1)
                con_cnt = con_cnt - 1

            Logger.LogIns().logger.info("***Check emq connected flag(before pub): " + str(self.emqConnectedFlag) + "***")
            if self.emqConnectedFlag:  # connect success
                self.doPublish(jsonMsg)

            self.client.disconnect()
            self.client.loop_stop()
            Logger.LogIns().logger.info("***do re-send Status data end.***")

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def sendApnsSilenceMsg(self):

        self.doSendApnsSilenceMsg()

        if self.sendSilenceMsgTimer is None:
            self.sendSilenceMsgTimer = QTimer()
            self.sendSilenceMsgTimer.setSingleShot(False)
            self.sendSilenceMsgTimer.timeout.connect(functools.partial(self.doSendApnsSilenceMsg))

            if self.device.freqAppAct > 0:
                self.sendSilenceMsgTimer.start(self.device.freqAppAct * 1000)  # unit: million seconds

    def doSendApnsSilenceMsg(self):

        Logger.LogIns().logger.info("***send Silence Msg Count: #" + str(self.sendSilenceMsgCount) + "***")
        if self.sendSilenceMsgCount > 0:
            Logger.LogIns().logger.info("***do Send Silence Msg: #" + str(self.sendSilenceMsgCount) + "***")
            self.FcmMsgProvider.doSendApnsSilenceMsg()
            self.sendSilenceMsgCount -= 1

            if self.adjSilenceMsgTimer:
                self.sendSilenceMsgTimer.setInterval((self.device.freqAppAct * 1000))
                Logger.LogIns().logger.info("***change freqAppAct: " + str((self.device.freqAppAct * 1000)) + " msecs ***")

        else:  # PPP finish sending message 30 times.
            self.mobileAppActiveFlag = False
            self.stopSendApnsSilenceMsgTimer()

    def stopSendApnsSilenceMsgTimer(self):
        if self.sendSilenceMsgTimer is not None:
            Logger.LogIns().logger.info("***STOP SEND Apns Silence MSG TIMER***")
            self.sendSilenceMsgTimer.stop()
            self.sendSilenceMsgTimer = None

    def sendEmqDeactivateMsg(self):
        msg = DevicePushMessageData.SilenceMessage()

        if self.device.mobileSolutionEnable is False:
            if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                if self.device.isNoneSN:
                    msg.SN = self.device.altSN
                else:
                    msg.SN = self.device.devicePropData.serialNumber.value

                msg.upsState = sysDef.UPS_StateMobile.Deactivate_PPP_mobile_solution.value
            else:  # if communication lost
                pass

        jsonMsg = msg.toJson()
        self.client = self.createClientInstance()
        self.client.connect(sysDef.EMQ_HOST, sysDef.EMQ_PORT, 60)
        self.client.loop_start()

        con_cnt = 30
        while con_cnt > 0:
            Logger.LogIns().logger.info("***In wait connection loop at " + str(abs(con_cnt - 30)) + " sec.(sendEmqDeactivateMsg)***")
            if self.emqConnectedFlag is True:
                break
            time.sleep(1)
            con_cnt = con_cnt - 1

        Logger.LogIns().logger.info("***Check emq connected flag(before pub): " + str(self.emqConnectedFlag) + "(sendEmqDeactivateMsg)***")
        if self.emqConnectedFlag:  # connect success
            self.doPublish(jsonMsg)

        self.client.disconnect()
        self.client.loop_stop()
        Logger.LogIns().logger.info("***do send emq deactivate msg end.***")

    def printLog(self, name, msg):
        Logger.LogIns().logger.info("***[EmqMsgProvider] printLog() {0} value = {1} ***".format(str(name), str(msg)))

    def selfTest(self):
        try:
            configData = self.device.deviceConfigure.configParam()
            configData.CMD_BATTERY_TEST = 1

            if self.device.deviceId != -1:  # 偵測到機器
                flag = self.device.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)
                valueIdFinder = ValueId.ValueIdFinder()
                if flag:  # 下cmd至機器成功
                    Logger.LogIns().logger.info("do self test start(cloud)")
                    trx = self.device.deviceConfigure.transactionData
                    if trx.statementsDic[valueIdFinder.getValueId("CMD_BATTERY_TEST")].errCode == 0:  # 機器回傳cmd執行成功
                        # 於此無法知道SelfTest執行結果, 只能知道有無執行
                        Logger.LogIns().logger.info("do self test(cloud)")
                        self.device.cloudBtestFlag = True
                    else:  # 機器回傳cmd執行失敗
                        # 目前只有log起來，之後要考慮將結果顯示在UI
                        Logger.LogIns().logger.info("do self test failed #1(cloud)")
                        self.device.cloudBtestFlag = False
                        self.device.cloudEvents.append(self.CloudEventID.ID_BATTERY_TEST_FAIL.value)
                else:  # 下cmd至機器失敗
                    # 目前只有log起來，之後要考慮將結果顯示在UI
                    Logger.LogIns().logger.info("do self test failed #2(cloud)")
                    self.device.cloudBtestFlag = False
                    self.device.cloudEvents.append(self.CloudEventID.ID_BATTERY_TEST_FAIL.value)


            else:  # 未偵測到機器
                Logger.LogIns().logger.info("do self test failed #3(cloud)")

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

class EmqEventProvider(QObject):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
        return class_._instance

    def __init__(self, device):
        super(EmqEventProvider, self).__init__()
        self.device = device
        self.CloudEventID = device.cloudEventId
        self.emqConnectedFlag = False
        self.emqAcc = None
        self.emqSecret = None
        self.EventMoble = EventsMobile.EventCloud(device)

        account = device.dataSource.readAppAccount()
        if account is not None and account.emqAcc is not None and account.emqSecret is not None:
            cryptor = DataCryptor.Cryptor()
            self.emqAcc = cryptor.decToString(account.emqAcc)
            self.emqSecret = cryptor.decToString(account.emqSecret)

        self.client = None

    def createClientInstance(self):
        client = mqtt.Client()

        # software communicate with EMQ production server by TLS protocol
        # if sysDef.BUILD_FOR is sysDef.BuildConfiguration.Production.value:
        my_ca_cert = os.path.join(settings.PROJECT_ROOT_PATH, "rootCA.crt")
        my_pri_cert = os.path.join(settings.PROJECT_ROOT_PATH, "d1.crt")
        my_key_cert = os.path.join(settings.PROJECT_ROOT_PATH, "d1.key")

        ssl.match_hostname = lambda cert, hostname: True
        client.tls_set(ca_certs=my_ca_cert, certfile=my_pri_cert, keyfile=my_key_cert,
                       tls_version=ssl.PROTOCOL_TLSv1_2,
                       ciphers=None)

        client.username_pw_set(self.emqAcc, self.emqSecret)

        # Callbacks are dependent on the client loop as without the loop the callbacks aren’t triggered.
        client.on_connect = self.on_connect
        return client

    # Event Connection acknowledged Triggers the on_connect callback
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.emqConnectedFlag = True
            Logger.LogIns().logger.info("***on_connect callback: EMQ server connected.***")
        else:
            self.emqConnectedFlag = False
            Logger.LogIns().logger.info(
                "***on_connect callback EMQ server connect failed with rc code= " + str(rc) + ".***")

    def doPublish(self, jsonMsg):
        if self.device.isNoneSN:
            pubTopic = "c/ppp-" + self.device.altSN + "/pub"
        else:
            pubTopic = "c/ppp-" + self.device.devicePropData.serialNumber.value + "/pub"

        Logger.LogIns().logger.info("***[doPublish]isNoneSN: " + str(self.device.isNoneSN) + "***")

        pub_result = self.client.publish(topic=pubTopic, payload=jsonMsg, qos=0, retain=False)

        Logger.LogIns().logger.info("***pub topic: " + str(pubTopic) + "***")
        Logger.LogIns().logger.info("***publish result: " + str(pub_result) + "***")

    def doStopLoop(self):
        # time.sleep(4)
        time.sleep(1)
        self.client.loop_stop()

    def doSendCurrentEmqStatusMsg(self, currentMsg):
        sendEmqMsgFlag = False  # True: send EMQ status message

        Logger.LogIns().logger.info("***into doSendCurrentEmqStatusMsg***")

        try:
            # satisfy conditions:  mobile solution enable, login success.
            if self.device.mobileSolutionEnable is True and self.device.mobileLoginState is True \
                    and self.device.topicId is not None:

                if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                    sendEmqMsgFlag = True
                else:  # if communication lost
                    Logger.LogIns().logger.info("EmqLostCommunicationMsgTimesLimit: " + str(self.device.EmqLostCommunicationMsgTimesLimit))
                    Logger.LogIns().logger.info("EmqLostCommunicationMsgCount: " + str(self.device.EmqLostCommunicationMsgCount))

                    # Lost Communication時, 送emq msg次數(count)由duration / interval決定, ex:60(sec)/15(sec)= 4(times)
                    if self.device.EmqLostCommunicationMsgCount < self.device.EmqLostCommunicationMsgTimesLimit:
                        sendEmqMsgFlag = True
                        Logger.LogIns().logger.info("***EMQ Status Msg LostCommunication Count: " + str(self.device.EmqLostCommunicationMsgCount) + "***")
                        self.device.EmqLostCommunicationMsgCount += 1

                if self.device.deviceId != -1 and self.device.isLostCommunication is False:  # if UPS plugged
                    if self.device.isNoneSN:
                        currentMsg.SN = self.device.altSN
                    else:
                        currentMsg.SN = self.device.devicePropData.serialNumber.value

                    Logger.LogIns().logger.info("***msg sn" + str(currentMsg.SN) + "***")

                    msg = currentMsg
                else:  # if communication lost
                    msg = DevicePushMessageData.SilenceMessage()
                    msg.SN = self.device.upsSN_Temp
                    msg.upsState = sysDef.UPS_StateMobile.Unable_to_establish_communication_with_UPS.value

                    self.device.cloudEvents.append(self.CloudEventID.ID_COMMUNICATION_LOST.value)
                    Logger.LogIns().logger.info("***doSendCurrentEmqStatusMsg ID_COMMUNICATION_LOST***")

                    msg.Event = self.EventMoble.GetEventObj(self.device.cloudEvents)

                    Logger.LogIns().logger.info("***msg sn: " + str(msg.SN) + "***")

                jsonMsg = msg.toJson()

                Logger.LogIns().logger.info("***emq slience msg: {0}***".format(jsonMsg))
                Logger.LogIns().logger.info("***do send Status data start.***")
                Logger.LogIns().logger.info("***Check emq connected flag(init): " + str(self.emqConnectedFlag) + "***")
                self.emqConnectedFlag = False
                self.client = self.createClientInstance()

                # do connect before start loop would be better.
                self.client.connect(sysDef.EMQ_HOST, sysDef.EMQ_PORT, 60)
                self.client.loop_start()  # loop_start() will re-connections automatically in the background every 3 to 6 seconds.

                con_cnt = 30  # wait x seconds for re-connections.
                while con_cnt > 0:  # wait in loop
                    Logger.LogIns().logger.info("***In wait connection loop at " + str(abs(con_cnt - 30)) + " sec.***")
                    if self.emqConnectedFlag is True:
                        break
                    time.sleep(1)
                    con_cnt = con_cnt - 1

                if self.emqConnectedFlag:  # connect success
                    Logger.LogIns().logger.info("***Need pub emq msg flag: " + str(sendEmqMsgFlag) + "***")
                    Logger.LogIns().logger.info("***Check emq connected flag(before pub): " + str(self.emqConnectedFlag) + "***")

                    if sendEmqMsgFlag is True:
                        self.doPublish(jsonMsg)

                    Logger.LogIns().logger.info("***Check emq connected flag(before disconnect): " + str(self.emqConnectedFlag) + "***")
                    self.client.disconnect()
                    self.doStopLoop()
                    Logger.LogIns().logger.info("***do send Status data end.***")
                else:
                    self.client.disconnect()
                    self.doStopLoop()

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
            self.doStopLoop()

            if sendEmqMsgFlag is True:
                Logger.LogIns().logger.info("***emq error catched do resend.***")

    def printLog(self, name, msg):
        Logger.LogIns().logger.info("***[EmqMsgProvider] printLog() {0} value = {1} ***".format(str(name), str(msg)))




