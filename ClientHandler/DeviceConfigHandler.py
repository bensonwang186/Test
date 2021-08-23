from PyQt5 import QtCore

from PyQt5.QtCore import QObject, pyqtSignal


class DeviceConfigHandler(QObject):
    def __init__(self, notificationPage, client, tray):
        super(DeviceConfigHandler, self).__init__()
        self.notificationPage = notificationPage
        self.client = client
        self.tray = tray
        self.initSlot()

    def initSlot(self):
        self.client.updateConfigSettingSignal.connect(self.setupChangedSlot)

    @QtCore.pyqtSlot(object)
    def setupChangedSlot(self, data):
        self.notificationPage.restoreSettings(data)
        self.tray.softwareSoundEnable = int(data.softwareSoundEnable)

        print("int(config.softwareSoundEnable)"+str(int(data.softwareSoundEnable)))
