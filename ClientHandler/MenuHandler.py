import sys
import traceback
from major import Command
from Utility import Logger

class MenuHandler(object):
    def __init__(self, masterPage, client, device):
        self.masterPage = masterPage
        self.device = device
        self.client = client
        self.client.showAppDisplaySignal.connect(self.openAppSlot)

    def openApp(self):
        try:
            self.client.queryRequest(Command.TARGET_SHOW_APP_DISPLAY)
        except Exception as e:
            Logger.LogIns().logger.error(e)

    def openAppSlot(self):
        try:
            self.masterPage.setHidden(False)
        except Exception as e:
            Logger.LogIns().logger.error(traceback.format_exc())