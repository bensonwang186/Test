import datetime
import json
import sys
import traceback

from System import settings, systemFunction
from Utility import Scheduler, Logger
from major import Command
from views.Custom import ViewData


class ScheduleHandler(object):
    def __init__(self, schedulePage, client):
        self.isShutdown = False
        self.schedulePage = schedulePage
        self.client = client
        # self.deviceConfigure = DeviceConfigure.DeviceConfigure()
        # self.schedulerManager = Scheduler.SchedulerManager()
        # self.initSchedule()  # 每次開機時, 重新設定排程

        # connect page signal for settings
        self.schedulePage.setScheduleSignal.connect(self.updateScheduleSlot)

        self.client.scheduleSettingUpdateSignal.connect(self.initSchedule)

    def initSchedule(self, data):
        # 每次開機時, 重新設定排程
        try:
            self.updateScheduleDisplay(data)  # 畫面更新, return tuple
            Logger.LogIns().logger.info("Initial schedule success")
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    # def restoreSchedule(self):
    #     try:
    #         self.device.dataSource.initScheduleSetting()  # db寫入設定
    #         data = self.updateScheduleDisplay()  # 畫面更新, return tuple
    #         self.schedulerManager.stopScheduleShutdownSchedule()
    #         self.isShutdown = False
    #         self.scheduleThreadProcess(data)
    #         logging.info("Restore schedule success")
    #     except Exception:
    #         traceback.print_exc(file=sys.stdout)

    def updateScheduleSlot(self, data):
        try:
            jsonData = json.dumps(data, ensure_ascii=False, default=systemFunction.jsonSerialize)
            Logger.LogIns().logger.info("Command.TARGET_SCHEDULE: " + jsonData)
            self.client.queryRequest(Command.TARGET_SET_SCHEDULE, jsonData)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def updateScheduleDisplay(self, data):
        oringDic = []

        displayDic = dict()
        # for item in data[0]:
        #     oringDic.append(Schedule(item))


        for item in data[0]:
            # displayDic[schData.days] = schData
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


        self.schedulePage.updateTable(displayDic)
        self.schedulePage.updateDescription(data[1], data[2])

        return data

    def scheduleThreadProcess(self, data):
        now = datetime.datetime.now()
        config = self.device.dataSource.readActiveConfig()

        # data[1]指關機時間, data[2]指開機時間
        if data[1] is not None and data[2] is None:  # 關機後不重新開機
            self.configData = configData = self.deviceConfigure.configParam()
            configData.CMD_SHUTDOWN = 1
            self.diff = diff = int((data[1].offTime - now).total_seconds())  # 幾秒後關機
            configData.params.append(settings.shutdownDuration)  # 倒數完 + 2分鐘後UPS關機(避免電腦早於UPS關機)
            self.schedulerManager.addScheduleShutdown(
                Scheduler.ScheduleThread("ScheduleShutdownThread", diff, config.shutDownType, configData,
                                         self.device.deviceId, self))
            self.schedulerManager.startScheduleShutdownSchedule()
            self.isShutdown = True

        elif data[1] is not None and data[2] is not None:  # 關機後重新開機
            self.configData = configData = self.deviceConfigure.configParam()
            configData.CMD_SHUTDOWN_RESTORE = 1
            self.diff = offDiff = int((data[1].offTime - now).total_seconds())  # 幾秒後關機
            configData.params.append(settings.shutdownDuration)  # 倒數完 + 2分鐘後UPS關機(避免電腦早於UPS關機)
            onDiff = int((data[2].onTime - data[1].offTime).total_seconds()) - settings.shutdownDuration  # 幾秒後開機
            configData.params.append(onDiff)

            self.schedulerManager.addScheduleShutdown(
                Scheduler.ScheduleThread("ScheduleShutdownThread", offDiff, config.shutDownType, configData,
                                         self.device.deviceId, self))
            self.schedulerManager.startScheduleShutdownSchedule()
            self.isShutdown = True

    def jsonSerialize(self, x):
        return x.toJson()