from ctypes import cdll

from System import settings


class ShutdownWin():
    def __init__(self):
        self.shutdownDll = cdll.LoadLibrary(settings.shutdownDll)

    def invoke(self):
        self.shutdownDll.invoke()
