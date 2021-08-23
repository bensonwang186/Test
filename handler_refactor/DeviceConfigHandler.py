import sys, os, traceback, configparser
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from model_Json.tables.Configuration import Configuration
from System import settings, systemFunction

class DeviceConfigHandler(QObject):
    def __init__(self, server, device):
        super(DeviceConfigHandler, self).__init__()
        self.server = server
        self.device = device
        self.initSlot()

    def initSlot(self):
        self.server.setAppDataPathSignal.connect(self.setAppDataPathSlot)

    @QtCore.pyqtSlot(object)
    def setAppDataPathSlot(self, setting):
        try:
            if (setting is None) or systemFunction.stringIsNullorEmpty(setting["iniPath"]) or systemFunction.stringIsNullorEmpty(setting["iniUser"]):
                return

            if os.path.isfile(settings.loggerIni):
                cp = configparser.ConfigParser()
                cp.read(settings.loggerIni)
                defaultPath = cp.get('DefaultSetting', 'app_data_path')
                defaultUser = cp.get('DefaultSetting', 'user')

                with open(settings.loggerIni, mode='w', encoding="utf-8") as cpFile:
                    if systemFunction.stringIsNullorEmpty(defaultPath):  # write once by first login user
                        cp.set("DefaultSetting", 'app_data_path', setting["iniPath"])

                    if systemFunction.stringIsNullorEmpty(defaultUser): # write once by first login user
                        cp.set("DefaultSetting", 'user', setting["iniUser"]) # update by current login user

                    cp.write(cpFile)
        except Exception:
            traceback.print_exc(file=sys.stdout)
