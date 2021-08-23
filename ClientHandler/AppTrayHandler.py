import sys, traceback
from major import Command

class AppTrayHandler(object):
    def __init__(self, appTray, client, device):
        self.appTray = appTray
        self.device = device
        self.client = client
        self.initFlag = True
        self.appTray.setlocaleSignal.connect(self.setsetlocaleSlot)

    def setsetlocaleSlot(self, locale):
        try:
            self.client.queryRequest(Command.TARGET_SET_LOCALE, locale)
        except Exception:
            traceback.print_exc(file=sys.stdout)