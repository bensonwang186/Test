
from PyQt5.QtCore import pyqtSignal, QObject

class DaemonStatus(QObject):

    daemonStatusUpdateSignal = pyqtSignal(object)

    def __init__(self):
        super(DaemonStatus, self).__init__(None)
        self._deviceId = -1
        self._isDaemonStarted = False
        self._shutdownType = -1
        self._shutdownTime = -1

    @property
    def shutdownType(self):
        return self._shutdownType

    @shutdownType.setter
    def shutdownType(self, value):
        self._shutdownType = value

    @property
    def shutdownTime(self):
        return self._shutdownTime

    @shutdownTime.setter
    def shutdownTime(self, value):
        self._shutdownTime = value

    @property
    def deviceId(self):
        return self._deviceId

    @deviceId.setter
    def deviceId(self, value):
        if value != self._deviceId:
            self._deviceId = value


    @property
    def isDaemonStarted(self):
        return self._isDaemonStarted

    @isDaemonStarted.setter
    def isDaemonStarted(self, value):
        if self.isDaemonStarted != value:
            self._isDaemonStarted = value
