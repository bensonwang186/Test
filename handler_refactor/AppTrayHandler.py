import sys
import traceback

from System import settings
from major import Command
from model_Json.tables.Configuration import Configuration


class AppTrayHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.server.setLanguageSignal.connect(self.setLanguageSlot)
        self.server.showAppDisplaySignal.connect(self.showAppDisplaySlot)

    def setLanguageSlot(self, param):
        try:
            config = Configuration()
            config.langSetting = param

            self.device.dataSource.updateDeviceConfig(config)

            # 與Client language設定檔同步
            with open(settings.langSetting, 'w') as file:
                file.write(param)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def showAppDisplaySlot(self):
        try:
            self.server.sendDataToClients(Command.TARGET_SHOW_APP_DISPLAY, True)
        except Exception:
            traceback.print_exc(file=sys.stdout)