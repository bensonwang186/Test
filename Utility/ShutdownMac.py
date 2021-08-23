from System import settings
import sys, os


class ShutdownMac():
    def __init__(self):
        pass

    def invoke(self):
        os.system("sh " + "\"" + settings.shutdownMac + "\"")
