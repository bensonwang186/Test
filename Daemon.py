import os,platform
import sys
import traceback
from PyQt5.QtCore import QCoreApplication

import controllers.TransactionHelper as helper
from System import settings, systemFunction, module
from controllers import DeviceMonitor
from handler_refactor import DeviceStatusHandler, NotificationHandler, DevicePropHandler, RuntimeHandler, VoltageHandler, AdvancedHandler, ScheduleHandler, SelfTestHandler, EnergyHandler, SummaryHandler, AppTrayHandler, EventLogsHandler, DeviceConfigHandler, SoftwareUpdateHandler
from major import AppServer
from model_Json import Device
from Utility import Logger

if platform.system() == 'Darwin':
    import signal
    # from py_objc.notificationCenterHandler import AppDelegate
    # from PyObjCTools import AppHelper

class Daemon:
    def __init__(self):
        module.Module(module=module.ModuleEnum.Deamon)
        # self.loop = asyncio.get_event_loop()
        self.app = QCoreApplication(sys.argv)
        self.device = None
        self.deviceStatusHandler = None
        self.model = None
        os.chdir(settings.PROJECT_ROOT_PATH)
        self.runner = None

    def start(self):
        try:
            self.device = Device.Device()
            Logger.LogIns().logger.info("***daemon start***")

            self.device.SMBiosUUID = systemFunction.getSMBiosUUID()
            self.device.ProcessorId = systemFunction.getProcessorId()
            self.device.dataSource.restore()
            self.device.dataSource.initScheduleSetting()  # 每次開機時, 重新設定排程

            helper.TransactionHelper().start()

            self.runner = AppServer.AppServerRunner(self.device)

            self.deviceStatusHandler = DeviceStatusHandler.DeviceStatusHandler(self.runner, self.device)
            self.devicePropHandler = DevicePropHandler.DevicePropHandler(self.runner, self.device)
            self.notifycationHandler = NotificationHandler.NotifycationHandler(self.runner, self.device)
            self.runtimeHandler = RuntimeHandler.RuntimeHandler(self.runner, self.device)
            self.voltageHandler = VoltageHandler.VoltageHandler(self.runner, self.device)
            self.advancedHandler = AdvancedHandler.AdvancedHandler(self.runner, self.device)
            self.scheduleHandler = ScheduleHandler.ScheduleHandler(self.runner, self.device)
            self.energyHandler = EnergyHandler.EnergyHandler(self.runner, self.device)
            self.selfTestHandler = SelfTestHandler.SelfTestHandler(self.runner, self.device)
            self.SummaryHandler = SummaryHandler.SummaryHandler(self.runner, self.device)
            self.AppTrayHandler = AppTrayHandler.AppTrayHandler(self.runner, self.device)
            self.EventLogsHandler = EventLogsHandler.EventLogsHandler(self.runner, self.device)
            self.DeviceConfigHandler = DeviceConfigHandler.DeviceConfigHandler(self.runner, self.device)
            self.software_update_handler = SoftwareUpdateHandler.SoftwareUpdateHandler(self.runner)

            self.model = DeviceMonitor.DeviceMonitor(self.runner, self.device)

            # if platform.system() == 'Darwin':
            #     signal.signal(signal.SIGTERM, self.handleSignal)
            #     signal.signal(signal.SIGINT, self.handleSignal)
            #     signal.signal(signal.SIGKILL, self.handleSignal)

        except Exception:
            traceback.print_exc(file=sys.stdout)

        sys.exit(self.app.exec_())

    def handleSignal(self, signum, frame):
        Logger.LogIns().logger.info("***daemon continue (Begin)***")
        Logger.LogIns().logger.info("signum: {0}".format(str(signum)))
        Logger.LogIns().logger.info("frame: {0}".format(str(frame)))

        if signum in (signal.SIGTERM, signal.SIGKILL, signal.SIGINT):
            Logger.LogIns().logger.info("***daemon termination (Begin)***")
            Logger.LogIns().logger.info(traceback.print_stack(frame))
            self.stop()
            Logger.LogIns().logger.info("***daemon termination (End)***")
            # AppHelper.CFRunLoopStop(AppHelper.CFRunLoopGetCurrent())

    def stop(self):
        Logger.LogIns().logger.info("***daemon stop (Begin)***")
        self.model.eventAnalyzer.occur(eventId=self.model.EventID.ID_COMMUNICATION_LOST)
        self.model.WebAppController.saveAndSendDeviceLog(False)
        Logger.LogIns().logger.info("***daemon stop (End)***")
        self.app.exit(0)
        # self.loop.shutdown_asyncgens()
        # self.loop.close()

    def deviceChanged(self, eventType, ptr, name):
        helper.TransactionHelper().driverTransaction.deviceChanged(eventType, ptr, name)

    def hibernate(self):
        Logger.LogIns().logger.info("***daemon sleep/Hibernate (Begin)***")
        self.model.dohibernate()
        Logger.LogIns().logger.info("***daemon sleep/Hibernate (End)***")

    def hibernateResume(self):
        Logger.LogIns().logger.info("***daemon Hibernate Resume (Begin)***")
        self.model.dohibernateResume()
        Logger.LogIns().logger.info("***daemon Hibernate Resume (End)***")

if __name__ == '__main__':

    daemon = Daemon()
    daemon.start()
    # AppHelper.CFRunLoopRun()
