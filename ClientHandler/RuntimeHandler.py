import sys
import traceback
from major import Command
from Utility import Logger

class RuntimeHandler(object):
    def __init__(self, runtimePage, client, daemonStatus, appTray):
        self.runtimePage = runtimePage
        self.client = client
        self.daemonStatus = daemonStatus
        self.appTray = appTray

        # connect page signal for settings
        self.runtimePage.setRuntimeSignal.connect(self.setRuntimeConfigSlot)

        # connect runtime config data signal for update
        self.client.updateConfigSettingSignal.connect(self.updateRuntimeConfigSlot)

    def updateRuntimeConfigSlot(self, config):
        self.runtimePage.restoreConfigSetting(config)
        self.daemonStatus.shutdownType = config.runtimeType
        self.daemonStatus.shutdownTime = config.runtimeCountdownTime

    def setRuntimeConfigSlot(self, runtimeType, runtimeCountdownTime):
        try:
            param = [runtimeType, runtimeCountdownTime]
            self.daemonStatus.shutdownType = runtimeType
            self.daemonStatus.shutdownTime = runtimeCountdownTime
            self.appTray.configChange(self.daemonStatus.shutdownType, self.daemonStatus.shutdownTime)
            self.client.queryRequest(Command.TARGET_SET_RUNTIME, param)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())