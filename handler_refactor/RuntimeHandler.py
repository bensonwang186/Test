import sys
import traceback
from model_Json.tables.Configuration import Configuration
from views.Custom import ViewData
from Utility import Logger

class RuntimeHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device

        # connect page signal for settings
        self.server.setRuntimeSignal.connect(self.setRuntimeConfigSlot)

        # connect runtime config data signal for update
    #     self.device.dataSource.updateConfigSettingSignal.connect(self.updateRuntimeConfigSlot)
    #
    # def updateRuntimeConfigSlot(self, config):
    #     self.runtimePage.restoreConfigSetting(config)

    def setRuntimeConfigSlot(self, runtimeType, runtimeCountdownTime):
        try:
            config = Configuration()
            config.runtimeType = runtimeType
            config.runtimeCountdownTime = runtimeCountdownTime
            self.device.dataSource.updateDeviceConfig(config)
            if config.runtimeType == ViewData.RuntimeSettingEnum.KeepComputerRunning.value:
                # self.device.deviceConfigure.setBatteryRuntime(runtimeCountdownTime * 60)
                configData = self.device.deviceConfigure.configParam()
                configData.SET_BATTERY_RUNTIME = 1
                configData.params.append(runtimeCountdownTime * 60)
                flag = self.device.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)

                if flag:
                    Logger.LogIns().logger.info("SET_BATTERY_RUNTIME success")
                else:
                    Logger.LogIns().logger.info("SET_BATTERY_RUNTIME fail")
        except Exception:
            traceback.print_exc(file=sys.stdout)