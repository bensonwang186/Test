from ctypes import cdll

from System import settings
import platform
import os
if platform.system() == 'Windows':
    import winsound
elif platform.system() == 'Darwin':
    import soundfile
    import sounddevice
from Utility import HibernateWin
from Utility import HibernateMac
from Utility import ShutdownWin
from Utility import ShutdownMac


class OSOperator(object):
    def __init__(self):
        self.shutdown = None
        self.hibernate = None
        self.beeper = None
        if platform.system() == 'Windows':
            self.shutdown = ShutdownWin.ShutdownWin()
            self.hibernate = HibernateWin.HibernateWin()
            self.beeper = BeeperWin()
        elif platform.system() == 'Darwin':
            self.shutdown = ShutdownMac.ShutdownMac()
            self.hibernate = HibernateMac.HibernateMac()
            self.beeper = BeeperMac()


    def doShudown(self):
        self.shutdown.invoke()
        # print("do Shutdown finish") # debug

    def doHibernate(self, delayMilliSec):
        self.hibernate.enter(delayMilliSec)
        # print("do Hibernate finish")  # debug

    def enableHibernate(self):
        self.hibernate.enable()

    def disableHibernate(self):
        self.hibernate.disable()

    def isHibernateSupport(self):
        return self.hibernate.isSupport()

    def isHibernateEnable(self):
        return self.hibernate.isEnable()

    def doBeep(self):
        return self.beeper.beep()


class BeeperWin(object):
    def __init__(self):
        print("beep win init")

    def beep(self):
        if platform.system() == 'Windows':
            duration = 5000  # millisecond
            freq = 2000  # Hz
            winsound.Beep(freq, duration)


class BeeperMac(object):
    def __init__(self):
        print("beep mac init")

    def beep(self):
        if platform.system() == 'Darwin':
            macAudioFile = '/System/Library/Sounds/Glass.aiff'
            if os.path.isfile(macAudioFile):
                data, fs = soundfile.read(macAudioFile)
                sounddevice.play(data, fs, blocking=True)
