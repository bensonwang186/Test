from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class DevicePropHandler(QObject):
    def __init__(self, masterPage, client, daemonStatus):
        super(DevicePropHandler, self).__init__()
        self.masterPage = masterPage
        self.client = client
        self.initSlot()

    def initSlot(self):
        self.client.updatePropertySignal.connect(self.propertiesChangedSlot)
        self.client.disableConfigureSignal.connect(self.disableConfigureSlot)

    @QtCore.pyqtSlot(object)
    def propertiesChangedSlot(self, data):
        self.masterPage.notificationPage.updatePageWithSocket(data)
        # self.masterPage.aboutPage.updatePageWithSocket(data)
        self.masterPage.runtimePage.updatePage(data)
        self.masterPage.aboutPage.updatePage(data)
        self.masterPage.voltagePage.updatePageWithSocket(data)
        self.masterPage.advancedPage.updatePageWithSocket(data)


    def disableConfigureSlot(self, data):
        self.masterPage.disableConfigure()

