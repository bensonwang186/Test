import datetime
import json
import sys
import traceback
import time
import platform

from System import settings, systemFunction
from Utility import Scheduler, Logger
from controllers import DeviceConfigure
from views.Custom import ViewData
from controllers import WebAppController
from Utility import Logger

class ScheduleHandler(object):
    def __init__(self, server, device):
        self.isShutdown = False
        self.device = device
        self.EventID = device.cloudEventId
        self.server = server
        self.deviceConfigure = DeviceConfigure.DeviceConfigure()
        # self.schedulerManager = Scheduler.SchedulerManager(device.desktopInteractiveServer)
        self.schedulerManager = self.device.schedulerManager
        self.WebAppController = WebAppController.WebAppController(device)
        self.initSchedule()  # 每次開機時, 重新設定排程

        # connect page signal for settings
        self.server.setScheduleSignal.connect(self.updateScheduleSlot)

    def initSchedule(self):
        # 每次開機時, 重新設定排程
        try:
            self.device.dataSource.initScheduleSetting()  # db寫入設定
            data = self.updateScheduleDisplay()  # 畫面更新, return tuple
            self.setDeviceSchedule(data)  # 設定排程開關機
            Logger.LogIns().logger.info("Initial schedule success")
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def restoreSchedule(self):
        try:
            self.device.dataSource.initScheduleSetting()  # db寫入設定
            data = self.updateScheduleDisplay()  # 畫面更新, return tuple
            self.schedulerManager.stopScheduleShutdownSchedule()
            self.isShutdown = False
            self.scheduleThreadProcess(data, 'restore')
            Logger.LogIns().logger.info("Restore schedule success")
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def updateScheduleSlot(self, data):
        try:
            displayDic = dict()
            for item in data:
                displayDic[item] = ViewData.ScheduleData(data[item])

            # 根據user設定, 更新排程

            self.device.dataSource.updateScheduleSetting(displayDic)  # db寫入設定
            data = self.updateScheduleDisplay()  # 畫面更新, return tuple
            self.setDeviceSchedule(data)  # 設定排程開關機

            from major import Command
            schData = self.device.dataSource.readScheduleSetting()
            jsonData = json.dumps(schData, ensure_ascii=False, default=systemFunction.jsonSerialize)
            # data = Command.TARGET_SCHEDULE + jsonData
            self.server.sendDataToClients(Command.TARGET_SCHEDULE, jsonData)
            print(jsonData)

            Logger.LogIns().logger.info("Update schedule success")
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def setDeviceSchedule(self, data):
        try:
            configData = self.deviceConfigure.configParam()
            configData.CMD_CANCEL_SCHEDULE = 1  # 先取消Schedule
            flag = self.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)

            self.schedulerManager.stopScheduleShutdownSchedule()
            self.isShutdown = False

            if flag:
                self.scheduleThreadProcess(data, None)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def updateScheduleDisplay(self):
        try:
            data = self.device.dataSource.readScheduleSetting()
            displayDic = dict()
            for item in data[0]:
                displayData = ViewData.ScheduleData()
                displayData.days = item.days
                displayData.onTimeHour = item.onTime.hour
                displayData.onTimeMin = item.onTime.minute
                displayData.onAction = item.onAction
                displayData.offTimeHour = item.offTime.hour
                displayData.offTimeMin = item.offTime.minute
                displayData.offAction = item.offAction
                displayData.noneReset = item.noneReset
                displayDic[item.days] = displayData

            jsonData = json.dumps(displayDic, ensure_ascii=False, default=systemFunction.jsonSerialize)
            displayDic2 = json.loads(jsonData)
            displayDic3 = dict()
            for key in displayDic2:
                displayDic3[key] = ViewData.ScheduleData(displayDic2[key])

            from major import Command
            clientJsonData = json.dumps(data, ensure_ascii=False, default=systemFunction.jsonSerialize)

            Logger.LogIns().logger.info("ALL SCHEDULE SHUTDOW SETTINGS: " + clientJsonData)
            self.server.sendDataToClients(Command.TARGET_SCHEDULE, clientJsonData)

            return data
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())


    def scheduleThreadProcess(self, data, scheduleType):
        try:
            now = datetime.datetime.now()
            config = self.device.dataSource.readActiveConfig()

            # data[1]指關機時間, data[2]指開機時間
            if data[1] is not None and data[2] is None:  # 關機後不重新開機
                Logger.LogIns().logger.info("set schedule off")
                self.configData = configData = self.deviceConfigure.configParam()
                configData.CMD_SHUTDOWN = 1

                self.diff = diff = int((data[1].offTime - now).total_seconds())  # 幾秒後關機
                Logger.LogIns().logger.info("set schedule off time: {}".format(data[1].offTime))
                Logger.LogIns().logger.info("set schedule now: {}".format(now))
                Logger.LogIns().logger.info("set schedule delay time: {}".format(self.diff))

                configData.params.append(settings.shutdownDuration)  # 倒數完 + 2分鐘後UPS關機(避免電腦早於UPS關機)
                Logger.LogIns().logger.info("set schedule configData: {}".format(configData.toJson()))

                self.schedulerManager.addScheduleShutdown(
                    Scheduler.ScheduleThread("ScheduleShutdownThread", diff, config.shutDownType, configData,
                                             self.device.deviceId, scheduleType, self))
                self.setEnterHibernation(config.shutDownType)
                self.schedulerManager.startScheduleShutdownSchedule()
                self.isShutdown = True

            elif data[1] is not None and data[2] is not None:  # 關機後重新開機
                Logger.LogIns().logger.info("set schedule off and on")
                self.configData = configData = self.deviceConfigure.configParam()
                configData.CMD_SHUTDOWN_RESTORE = 1

                self.diff = offDiff = int((data[1].offTime - now).total_seconds())  # 幾秒後關機
                Logger.LogIns().logger.info("set schedule off time: {}".format(data[1].offTime))
                Logger.LogIns().logger.info("set schedule on time: {}".format(data[2].onTime))
                Logger.LogIns().logger.info("set schedule now: {}".format(now))
                Logger.LogIns().logger.info("set schedule delay time: {}".format(self.diff))

                configData.params.append(settings.shutdownDuration)  # 倒數完 + 2分鐘後UPS關機(避免電腦早於UPS關機)
                onDiff = int((data[2].onTime - data[1].offTime).total_seconds()) - settings.shutdownDuration  # 幾秒後開機
                configData.params.append(onDiff)

                Logger.LogIns().logger.info("set schedule configData: {}".format(configData.toJson()))

                self.schedulerManager.addScheduleShutdown(
                    Scheduler.ScheduleThread("ScheduleShutdownThread", offDiff, config.shutDownType, configData,
                                             self.device.deviceId, scheduleType, self))
                self.setEnterHibernation(config.shutDownType)
                self.schedulerManager.startScheduleShutdownSchedule()
                self.isShutdown = True
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def setEnterHibernation(self, shutdownType):
        if int(shutdownType) == ViewData.ShutdownTypeEnum.Hibernation.value:
            self.device.enterHibernation = True

    def sendExpiredEvent(self):

        self.device.cloudEventsTemp.append(self.CloudEventID.ID_SCHEDULE_EXPIRED.value)

        Logger.LogIns().logger.info("***[ScheduleHandler] begin sleep***")
        time.sleep(6)

        Logger.LogIns().logger.info("***[ScheduleHandler] begin check thread complete***")
        Logger.LogIns().logger.info("***[ScheduleHandler] emqMsgThreadPool length: {0} ***".format(str(len(self.schedulerManager.emqMsgThreadPool))))
        Logger.LogIns().logger.info("***[ScheduleHandler] deviceLogThreadPool length: {0} ***".format(str(len(self.schedulerManager.deviceLogThreadPool))))

        f1 = self.schedulerManager.checkDeviceLogThreadComplete()
        f2 = self.schedulerManager.checkEmqMsgThreadComplete()

        Logger.LogIns().logger.info("***[ScheduleHandler] f1 flag: {0} ***".format(str(f1)))
        Logger.LogIns().logger.info("***[ScheduleHandler] f2 flag: {0} ***".format(str(f2)))

    def sendScheduleShutdownEvent(self):
        self.server.eventOccurSignal.emit(self.EventID.ID_SCHEDULE_EXPIRED)

        if platform.system() == 'Darwin':
            self.server.shutdownAlertSignal.emit(self.EventID.ID_COMMUNICATION_LOST)

        self.WebAppController.saveAndSendDeviceLog(False)
