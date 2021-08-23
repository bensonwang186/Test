import sys
import threading
import time
import traceback
import platform
from threading import Condition

from System import systemFunction
from Utility import EmailSender, i18nTranslater, OSOperator
from controllers import DeviceConfigure
from i18n import appLocaleData
from model_Json import DataSource2
from views.Custom import ViewData
from views.Custom.ViewData import ShutdownTypeEnum
from Utility import DataCryptor
from PyQt5.QtCore import QTimer
from Utility import Logger
class SchedulerManager:
    shutdownThreadPool = []
    sendEmailThreadPool = []
    requestOauthThreadPool = []
    scheduleShutdownThreadPool = []
    # energyConsumptionThreadPool = []
    deviceLogThreadPool = []
    emqMsgThreadPool = []
    batteryTestThreadPool = []
    webLoginThreadPool = []

    def __init__(self, desktopInteractiveServer):
        self.desktopInteractiveServer = desktopInteractiveServer

    def addShutdownSchedule(self, Thread):
        self.shutdownThreadPool.append(Thread)

    def startShutdownSchedule(self):
        temp = []
        for sendMailThread in self.sendEmailThreadPool:
            try:
                sendMailThread.join(30)  # join email timeout is 30 sec, if 30sec not send mail, give it up
            except:
                Logger.LogIns().logger.info("sendMailThread join failed")
        for shutdownThraed in self.shutdownThreadPool:
            if not shutdownThraed.isStop:
                Logger.LogIns().logger.info("shutdownThraed start")
                try:
                    shutdownThraed.start()
                except Exception:
                    Logger.LogIns().logger.info("except")
                    Logger.LogIns().logger.info("startShutdownSchedule {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("shutdownThraed stop")
            else:
                temp.append(shutdownThraed)

        for shutdownTemp in temp:
            try:
                self.shutdownThreadPool.remove(shutdownTemp)
            except Exception:
                Logger.LogIns().logger.info("remove shutdown thread error")

    def isShutdownExcuting(self):
        return len(self.shutdownThreadPool) > 0

    def stopShutdownSchedule(self):
        for shudownThread in self.shutdownThreadPool:
            shudownThread.cancel()

    def addSendMailSchedule(self, Thread):
        self.sendEmailThreadPool.append(Thread)

    def startSendMailSchedule(self):
        temp = []
        Logger.LogIns().logger.info("start send")
        Logger.LogIns().logger.info("thread size" + str(len(self.sendEmailThreadPool)))
        for sendEmailThread in self.sendEmailThreadPool:
            Logger.LogIns().logger.info("run start" + str(sendEmailThread.isAlive))
            if not sendEmailThread.isStop and not sendEmailThread.isStart:
                try:
                    sendEmailThread.start()
                except Exception:
                    Logger.LogIns().logger.info("except")
                    Logger.LogIns().logger.info("startSendMailSchedule {}".format(traceback.format_exc()))
            else:
                Logger.LogIns().logger.info("need remove thread")
                temp.append(sendEmailThread)
                Logger.LogIns().logger.info("run end")

        for sendTemp in temp:
            self.sendEmailThreadPool.remove(sendTemp)

    def addScheduleShutdown(self, Thread):
        self.scheduleShutdownThreadPool.append(Thread)

    def startScheduleShutdownSchedule(self):
        temp = []
        for scheduleThraed in self.scheduleShutdownThreadPool:
            if not scheduleThraed.isStop:
                Logger.LogIns().logger.info("scheduleThraed start")
                try:
                    scheduleThraed.start()
                except Exception:
                    Logger.LogIns().logger.info("except")
                    Logger.LogIns().logger.info("scheduleThraed {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("scheduleThraed stop")
            else:
                temp.append(scheduleThraed)

        for shutdownTemp in temp:
            try:
                self.scheduleShutdownThreadPool.remove(shutdownTemp)
            except Exception:
                Logger.LogIns().logger.info("remove shutdown thread error")

        print("thread pool length: " + str(len(self.scheduleShutdownThreadPool)))

    def stopScheduleShutdownSchedule(self):
        for scheduleThread in self.scheduleShutdownThreadPool:
            scheduleThread.cancel()

    def addDeviceLogSchedule(self, Thread):
        self.deviceLogThreadPool.append(Thread)

    def startDeviceLogSchedule(self):
        temp = []
        for logThraed in self.deviceLogThreadPool:
            if not logThraed.isStop:
                Logger.LogIns().logger.info("Device Log thraed start")
                print("Device Log thraed delayTime: " + str(systemFunction.formatTime(logThraed.delayTime)))
                print("Device Log thraed alive: " + str(logThraed.isAlive()))

                # Avoid RuntimeError: threads can only be started once
                if logThraed.isAlive() is False:  # isAlive() to check if a thread is still running
                    try:
                        logThraed.start()
                    except Exception:
                        Logger.LogIns().logger.info("except")
                        Logger.LogIns().logger.info("startDeviceLogSchedule {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("Device Log thraed stop")
            else:
                temp.append(logThraed)

        for logTemp in temp:
            try:
                self.deviceLogThreadPool.remove(logTemp)
            except Exception:
                Logger.LogIns().logger.info("remove Device Log thread error")

        print("thread pool length: " + str(len(self.deviceLogThreadPool)))

    def stopDeviceLogSchedule(self):
        for logThraed in self.deviceLogThreadPool:
            logThraed.cancel()

    def checkDeviceLogThreadComplete(self):
        print("deviceLogThreadPool length: " + str(len(self.deviceLogThreadPool)))
        for thread in self.deviceLogThreadPool:
            thread.join(30)

        return True

    def addEmqMsgSchedule(self, Thread):
        self.emqMsgThreadPool.append(Thread)

    def startEmqMsgSchedule(self):
        temp = []
        for msgThraed in self.emqMsgThreadPool:
            if not msgThraed.isStop:
                Logger.LogIns().logger.info("Emq msg thraed start")
                print("Emq msg thraed delayTime: " + str(systemFunction.formatTime(msgThraed.delayTime)))
                print("Emq msg thraed alive: " + str(msgThraed.isAlive()))

                # Avoid RuntimeError: threads can only be started once
                if msgThraed.isAlive() is False:  # isAlive() to check if a thread is still running
                    try:
                        msgThraed.start()
                    except Exception:
                        Logger.LogIns().logger.info("except")
                        Logger.LogIns().logger.info("startEmqMsgSchedule {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("Emq msg thraed stop")
            else:
                temp.append(msgThraed)

        for msgTemp in temp:
            try:
                self.emqMsgThreadPool.remove(msgTemp)
            except Exception:
                Logger.LogIns().logger.info("remove Emq msg thread error")

        print("thread pool length: " + str(len(self.emqMsgThreadPool)))

    def stopEmqMsgSchedule(self):
        for logThraed in self.emqMsgThreadPool:
            logThraed.cancel()

    def checkEmqMsgThreadComplete(self):
        print("emqMsgThreadPool length: " + str(len(self.emqMsgThreadPool)))
        for thread in self.emqMsgThreadPool:
            thread.join(30)

        return True

    def addBatteryTestSchedule(self, Thread):
        self.batteryTestThreadPool.append(Thread)

    def startBatteryTestSchedule(self):
        temp = []
        for msgThraed in self.batteryTestThreadPool:
            if not msgThraed.isStop:
                Logger.LogIns().logger.info("Battery Test thraed start")
                print("Battery Test thraed delayTime: " + str(systemFunction.formatTime(msgThraed.delayTime)))
                print("Battery Test thraed alive: " + str(msgThraed.isAlive()))

                # Avoid RuntimeError: threads can only be started once
                if msgThraed.isAlive() is False:  # isAlive() to check if a thread is still running
                    try:
                        msgThraed.start()
                    except Exception:
                        Logger.LogIns().logger.info("except")
                        Logger.LogIns().logger.info("startBatteryTestSchedule {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("Battery Test thraed stop")
            else:
                temp.append(msgThraed)

        for msgTemp in temp:
            try:
                self.batteryTestThreadPool.remove(msgTemp)
            except Exception:
                Logger.LogIns().logger.info("remove Battery Test thread error")

        print("thread pool length: " + str(len(self.batteryTestThreadPool)))

    def stopBatteryTestSchedule(self):
        for bTestThraed in self.batteryTestThreadPool:
            bTestThraed.cancel()

    def addWebLoginSchedule(self, Thread):
        self.webLoginThreadPool.append(Thread)

    def startWebLoginSchedule(self):
        temp = []
        for theThread in self.webLoginThreadPool:
            if not theThread.isStop:
                Logger.LogIns().logger.info("Web Login Thread start")
                # Avoid RuntimeError: threads can only be started once
                if theThread.isAlive() is False:  # isAlive() to check if a thread is still running
                    Logger.LogIns().logger.info(theThread)
                    try:
                        theThread.start()
                    except Exception:
                        Logger.LogIns().logger.info("except")
                        Logger.LogIns().logger.info("startWebLoginSchedule {}".format(traceback.format_exc()))
                Logger.LogIns().logger.info("Web Login Thread stop")
            else:
                temp.append(theThread)

        for msgTemp in temp:
            try:
                self.webLoginThreadPool.remove(msgTemp)
            except Exception:
                Logger.LogIns().logger.info("remove Battery Test thread error")

        print("thread pool length: " + str(len(self.webLoginThreadPool)))

    def stopWebLoginSchedule(self):
        for theThread in self.webLoginThreadPool:
            theThread.cancel()

class ShutdownThread(threading.Thread):
    con = Condition()

    # def __init__(self, threadName, delayTime, shutdownType, desktopInteractiveServer, configData, deviceId, handler):
    def __init__(self, threadName, delayTime, shutdownUtil):
        super(ShutdownThread, self).__init__(name=threadName)
        # self.eventHandler = handler
        # self.desktopInteractiveServer = desktopInteractiveServer
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        # self.shutdownType = shutdownType
        self.isStop = False
        # self.configData = configData
        # self.deviceId = deviceId
        self.shutdownUtil = shutdownUtil


    def run(self):
        # delay thread via wait
        with self.con:
            self.con.wait(self.delayTime)
        if not self.stopEvent.is_set() or not self.isStop:
            self.shutdownUtil.doShutdown()
            # self.doShutdown(self.shutdownType)
            self.isStop = True

    def cancel(self):
        self.stopEvent.set()
        self.isStop = True

        with self.con:
            self.con.notify()

    # def doShutdown(self, shutdownType):
    #
    #     # -----------------------設定UPS開關機-----------------------
    #     print("do UPS Shutdown")
    #     # 設定UPS關機需在PC關機前, 但實際UPS關機行為需在PC關機後(UPS delay 2 mins關機)
    #     flag = DeviceConfigure.DeviceConfigure().deviceConfigSubmit(self.configData, self.deviceId)
    #
    #     self.eventHandler.sendShutdownEvent()
    #
    #     # -----------------------設定PC關機-----------------------
    #     if int(shutdownType) == ShutdownTypeEnum.Shutdown.value:
    #         if platform.system() == 'Windows':
    #             if self.desktopInteractiveServer.logout():
    #                 time.sleep(30)  # pause 5.5 seconds
    #         OSOperator.OSOperator().doShudown()
    #     elif int(shutdownType) == ShutdownTypeEnum.Hibernation.value:
    #         OSOperator.OSOperator().doHibernate(1000)
    #
    # def ss(self):
    #     OSOperator.OSOperator().doShudown()

class SendMailThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, emailNotification, ouathCredential, eventId, isTest, isVerify=None, callBack=None, isHwFault= None, errorCode= None):
        super(SendMailThread, self).__init__(name=threadName)
        self.stopEvent = threading.Event()
        self.eventId = eventId
        self.emailNotification = emailNotification
        self.ouathCredential = ouathCredential
        self.isStop = False
        self.isStart = False
        self.isTest = isTest
        self.isVerify = isVerify
        self.isHwFault = isHwFault
        self.errorCode = errorCode
        self.callBack = callBack

    def run(self):
        self.isStart = True
        # delay thread via wait
        if self.isTest:
            Logger.LogIns().logger.info("start test send mail")
            Logger.LogIns().logger.info("event id: "+str(self.eventId))
            self.doTestSend()
        elif self.isVerify:
            self.doVerify()
        else:
            self.doSend()

        self.isStop = True

    def cancel(self):
        self.isStop = True
        self.stopEvent.set()

    def doTestSend(self):
        cryptor = DataCryptor.Cryptor()
        if self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.GMAIL.value:
            EmailSender.EmailSender().sendEmailByOauth("This is a test mail.", self.emailNotification.senderName,
                                                       self.emailNotification.receivers,
                                                       cryptor.decToString(self.ouathCredential.accessToken),
                                                       cryptor.decToString(self.ouathCredential.clientId),
                                                       cryptor.decToString(self.ouathCredential.clientSecret),
                                                       cryptor.decToString(self.ouathCredential.refreshToken),
                                                       self.ouathCredential.tokenExpiry,
                                                       cryptor.decToString(self.ouathCredential.tokenUri),
                                                       self.callBack)
        elif self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.OTHER.value:
            EmailSender.EmailSender().sendEmail("This is a test mail.", self.emailNotification.smtpServiceAddress,
                                                self.emailNotification.securityConnection,
                                                self.emailNotification.servicePort,
                                                self.emailNotification.senderName,
                                                self.emailNotification.senderEmailAddress,
                                                self.emailNotification.needAuth,
                                                self.emailNotification.authAccount,
                                                cryptor.decToString(self.emailNotification.authPassword),
                                                self.emailNotification.receivers,
                                                self.callBack)

    def doVerify(self):
        cryptor = DataCryptor.Cryptor()
        if self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.GMAIL.value:
            EmailSender.EmailSender().sendEmailByOauth("This is a test mail.", self.emailNotification.senderName,
                                                       "",
                                                       cryptor.decToString(self.ouathCredential.accessToken),
                                                       cryptor.decToString(self.ouathCredential.clientId),
                                                       cryptor.decToString(self.ouathCredential.clientSecret),
                                                       cryptor.decToString(self.ouathCredential.refreshToken),
                                                       self.ouathCredential.tokenExpiry,
                                                       cryptor.decToString(self.ouathCredential.tokenUri),
                                                       self.callBack,
                                                       isVerify=True)
        elif self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.OTHER.value:
            EmailSender.EmailSender().sendEmail("This is a test mail.", self.emailNotification.smtpServiceAddress,
                                                self.emailNotification.securityConnection,
                                                self.emailNotification.servicePort,
                                                self.emailNotification.senderName,
                                                self.emailNotification.senderEmailAddress,
                                                self.emailNotification.needAuth,
                                                self.emailNotification.authAccount,
                                                cryptor.decToString(self.emailNotification.authPassword),
                                                self.emailNotification.senderEmailAddress,
                                                self.callBack)

    def doSend(self):

        # send email
        message = i18nTranslater.MessageCoverter().coveterEventMessage(appLocaleData.appLocaleRecorderFromDB().appLocale,self.eventId.value)
        if self.isHwFault and (self.errorCode is not None and len(self.errorCode) >0):
            errCodeDescription = i18nTranslater.MessageCoverter().coveterEventCodeMessage(appLocaleData.appLocaleRecorderFromDB().appLocale, self.errorCode)
            if len(errCodeDescription) > 0:
                message += " : "
                message += errCodeDescription

        cryptor = DataCryptor.Cryptor()
        if self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.GMAIL.value:
            EmailSender.EmailSender().sendEmailByOauth(message, self.emailNotification.senderName,
                                                       self.emailNotification.receivers,
                                                       cryptor.decToString(self.ouathCredential.accessToken),
                                                       cryptor.decToString(self.ouathCredential.clientId),
                                                       cryptor.decToString(self.ouathCredential.clientSecret),
                                                       cryptor.decToString(self.ouathCredential.refreshToken),
                                                       self.ouathCredential.tokenExpiry,
                                                       cryptor.decToString(self.ouathCredential.tokenUri),
                                                       self.callBack)
        elif self.emailNotification.serviceProvider == DataSource2.EmailServiceProvider.OTHER.value:
            EmailSender.EmailSender().sendEmail(message, self.emailNotification.smtpServiceAddress,
                                                self.emailNotification.securityConnection,
                                                self.emailNotification.servicePort,
                                                self.emailNotification.senderName,
                                                self.emailNotification.senderEmailAddress,
                                                self.emailNotification.needAuth,
                                                self.emailNotification.authAccount,
                                                cryptor.decToString(self.emailNotification.authPassword),
                                                self.emailNotification.receivers,
                                                self.callBack)

class ScheduleThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, delayTime, shutdownType, configData, deviceId, scheduleType, handler):
        super(ScheduleThread, self).__init__(name=threadName)
        self.scheduleHandler = handler
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        self.shutdownType = shutdownType
        self.configData = configData
        self.deviceId = deviceId
        self.scheduleType = scheduleType
        self.isStop = False

    def run(self):
        Logger.LogIns().logger.info("Start schedule shutdown")
        Logger.LogIns().logger.info("thread id {}".format(threading.current_thread().ident))
        Logger.LogIns().logger.info("start time {}".format(time.time()))
        Logger.LogIns().logger.info("delay time {}".format(self.delayTime))

        try:
            # delay thread via wait
            with self.con:
                self.con.wait(self.delayTime)
            # time.sleep(self.delayTime)
            if not self.stopEvent.is_set() or not self.isStop:
                self.doSchedule(self.shutdownType)
                self.isStop = True
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def cancel(self):
        try:
            self.stopEvent.set()
            self.isStop = True

            with self.con:
                self.con.notify()
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def doSchedule(self, shutdownType):

        # -----------------------設定UPS開關機-----------------------
        Logger.LogIns().logger.info("do UPS Shutdown")
        # 設定UPS關機需在PC關機前, 但實際UPS關機行為需在PC關機後(UPS delay 2 mins關機)
        flag = DeviceConfigure.DeviceConfigure().deviceConfigSubmit(self.configData, self.deviceId)
        Logger.LogIns().logger.info("Config Submit flag: " + str(flag))

        if self.scheduleType == None:
            self.scheduleHandler.sendScheduleShutdownEvent()

        # -----------------------設定PC關機-----------------------
        if int(shutdownType) == ShutdownTypeEnum.Shutdown.value:
            Logger.LogIns().logger.info("do PC shutdown")
            OSOperator.OSOperator().doShudown()
        elif int(shutdownType) == ShutdownTypeEnum.Hibernation.value:
            self.scheduleHandler.restoreSchedule()  # 更新Schedule

            if self.scheduleType == 'restore':
                for x in range(5, -1, -1):
                    time.sleep(1)
                    print(systemFunction.formatTime(x))
                    if x == 0:
                        print("do PC hibernation")
                        Logger.LogIns().logger.info("do PC hibernation")
                        OSOperator.OSOperator().doHibernate(1000)

class DeviceLogThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, delayTime, handler, dcode, endDate):
        super(DeviceLogThread, self).__init__(name=threadName)
        self.webAppController = handler
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        self.dcode = dcode
        self.endDate = endDate
        self.isStop = False

    def run(self):
        try:
            # delay thread via wait
            with self.con:
                self.con.wait(self.delayTime)
            # time.sleep(self.delayTime)
            if not self.stopEvent.is_set() or not self.isStop:
                self.doInsertLogs(self.dcode, self.endDate)
                self.isStop = True
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cancel(self):
        self.stopEvent.set()
        self.isStop = True

        with self.con:
            self.con.notify()

    def doInsertLogs(self, dcode, endDate):
        self.webAppController.printLog("DeviceLogThread", "***********addDeviceLogApp start***********")
        response = self.webAppController.addDeviceLogApp(dcode, endDate)
        self.webAppController.printLog("DeviceLogThread", "***********addDeviceLogApp finish***********")

class EmqMsgThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, delayTime, handler, msg):
        super(EmqMsgThread, self).__init__(name=threadName)
        self.handler = handler
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        self.isStop = False
        self.msg = msg  # current status message

    def run(self):
        try:
            # delay thread via wait
            with self.con:
                self.con.wait(self.delayTime)

            if not self.stopEvent.is_set() or not self.isStop:
                self.doSendEmqMsg(self.msg)
                self.isStop = True
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cancel(self):
        self.stopEvent.set()
        self.isStop = True

        with self.con:
            self.con.notify()

    def doSendEmqMsg(self, msg):
        self.handler.printLog("EmqMsgThread", "***********doSendEmqMsg start***********")
        self.handler.doSendCurrentEmqStatusMsg(msg)
        self.handler.printLog("EmqMsgThread", "***********doSendEmqMsg finish***********")

class BatteryTestThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, delayTime, handler):
        super(BatteryTestThread, self).__init__(name=threadName)
        self.EmqMsgProvider = handler
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        self.isStop = False

    def run(self):
        try:
            # delay thread via wait
            with self.con:
                self.con.wait(self.delayTime)

            if not self.stopEvent.is_set() or not self.isStop:
                self.doBatteryTest()
                self.isStop = True
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cancel(self):
        self.stopEvent.set()
        self.isStop = True

        with self.con:
            self.con.notify()

    def doBatteryTest(self):
        self.EmqMsgProvider.printLog("BatteryTestThread", "***********doBatteryTest start***********")
        self.EmqMsgProvider.selfTest()
        self.EmqMsgProvider.printLog("BatteryTestThread", "***********doBatteryTest finish***********")

class WebLoginThread(threading.Thread):
    con = Condition()

    def __init__(self, threadName, delayTime, handler):
        super(WebLoginThread, self).__init__(name=threadName)
        self.handler = handler
        self.stopEvent = threading.Event()
        self.delayTime = delayTime
        self.isStop = False

    def run(self):
        try:
            # delay thread via wait
            with self.con:
                self.con.wait(self.delayTime)

            if not self.stopEvent.is_set() or not self.isStop:
                self.handler.ResetMobileLogin()
                self.isStop = True
        except Exception:
            Logger.LogIns().logger.info("WebLoginThread {}".format(traceback.format_exc()))
            traceback.print_exc(file=sys.stdout)

    def cancel(self):
        self.stopEvent.set()
        self.isStop = True

        with self.con:
            self.con.notify()
