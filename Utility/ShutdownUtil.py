import time
import platform
from Utility import OSOperator
from controllers import DeviceConfigure
from views.Custom.ViewData import ShutdownTypeEnum

class ShutdownUtil:
    def __init__(self, shutdownType, configData, desktopInteractiveServer, deviceId, handler):
        self.configData = configData
        self.deviceId = deviceId
        self.shutdownType = shutdownType
        self.desktopInteractiveServer = desktopInteractiveServer
        self.eventHandler = handler

    def doShutdown(self):

        # -----------------------設定UPS開關機-----------------------
        print("do UPS Shutdown")
        # 設定UPS關機需在PC關機前, 但實際UPS關機行為需在PC關機後(UPS delay 2 mins關機)
        flag = DeviceConfigure.DeviceConfigure().deviceConfigSubmit(self.configData, self.deviceId)

        if self.eventHandler.outputStopSoon == 0:
            self.eventHandler.sendShutdownEvent()

        # -----------------------設定PC關機-----------------------
        if int(self.shutdownType) == ShutdownTypeEnum.Shutdown.value:
            if platform.system() == 'Windows':
                if self.desktopInteractiveServer.logout():
                    time.sleep(30)  # pause 5.5 seconds
            OSOperator.OSOperator().doShudown()
        elif int(self.shutdownType) == ShutdownTypeEnum.Hibernation.value:
            OSOperator.OSOperator().doHibernate(1000)