from System import settings
import sys, os
import time

class HibernateMac():
    def __init__(self):
        pass

    def isSupport(self):
        return True

    def isEnable(self):
        return True

    def enable(self):
        return False

    def disable(self):
        return False

    def enter(self, delayMilliSec):
        time.sleep(delayMilliSec / 1000)
        os.system("sh " + "\"" + settings.hibernateMac + "\"")

