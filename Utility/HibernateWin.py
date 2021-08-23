from ctypes import cdll, c_long

from System import settings


class HibernateWin():
    def __init__(self):
        self.hibernateDll = cdll.LoadLibrary(settings.hibernateDll)
        self.hibernateDll.enter.argtypes = [c_long]

    def isSupport(self):
        return self.hibernateDll.supported()

    def isEnable(self):
        return self.hibernateDll.isEnabled()

    def enable(self):
        return self.hibernateDll.enable()

    def disable(self):
        return self.hibernateDll.disable()

    def enter(self, delayMilliSec):
        self.hibernateDll.enter(delayMilliSec)
