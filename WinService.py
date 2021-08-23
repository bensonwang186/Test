import datetime
import os
import sys
import traceback

import servicemanager
import win32event
import win32gui
import win32gui_struct
import win32service
import win32serviceutil

import Daemon
from System import settings, module
from Utility import Logger

struct = win32gui_struct.struct
pywintypes = win32gui_struct.pywintypes
import win32con

GUID_DEVINTERFACE_USB_DEVICE = "{4D1E55B2-F16F-11CF-88CB-001111000030}"

# ref.: https://docs.microsoft.com/en-us/windows/win32/devio/wm-devicechange
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEREMOVECOMPLETE = 0x8004

# ref.: https://docs.microsoft.com/en-us/windows/win32/termserv/wm-wtssession-change
WTS_SESSION_LOGON = 0x5
WTS_SESSION_LOGOFF = 0x6
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8

# ref.: https://docs.microsoft.com/en-us/windows/win32/power/wm-powerbroadcast
PBT_APMPOWERSTATUSCHANGE = 0xA
PBT_APMRESUMEAUTOMATIC = 0x12
PBT_APMRESUMESUSPEND = 0x7
PBT_APMSUSPEND = 0x4
PBT_POWERSETTINGCHANGE = 0x8013

import ctypes

ServiceName = "PowerPanel Personal Service"
ServiceDisplayName = "PowerPanel Personal Service"
ServiceDescription = "PowerPanel Personal Service monitors and controls the CyberPower UPS."

def delDebugFile():
    try:
        debugFile = os.path.join(settings.PROJECT_ROOT_PATH, "winservice_log.txt")
        if os.path.isfile(debugFile):
            os.remove(debugFile)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)

def writeDebugMsg(msg):
    try:
        isConfigExist = os.path.isfile("log.json")
        if isConfigExist:
            debugFile = os.path.join(settings.PROJECT_ROOT_PATH, "winservice_log.txt")
            if not os.path.isfile(debugFile):
                with open(debugFile, 'w'):  # create a empty file
                    pass

            with open(debugFile, 'r') as file:
                contents = file.readlines()

            index = len(contents) + 1
            contents.insert(index, (msg + "\n"))

            with open(debugFile, 'w') as file:
                contents = "".join(contents)
                file.write(contents)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


def _UnpackDEV_BROADCAST(lparam):
    if lparam == 0: return None
    hdr_format = "iii"
    hdr_size = struct.calcsize(hdr_format)
    hdr_buf = win32gui.PyGetMemory(lparam, hdr_size)
    size, devtype, reserved = struct.unpack("iii", hdr_buf)
    # Due to x64 alignment issues, we need to use the full format string over
    # the entire buffer.  ie, on x64:
    # calcsize('iiiP') != calcsize('iii')+calcsize('P')
    buf = win32gui.PyGetMemory(lparam, size)

    extra = {}
    if devtype == win32con.DBT_DEVTYP_DEVICEINTERFACE:
        fmt = hdr_format + "16s"
        _, _, _, guid_bytes = struct.unpack(fmt, buf[:struct.calcsize(fmt)])
        extra['classguid'] = pywintypes.IID(guid_bytes, True)
        extra['name'] = ctypes.wstring_at(lparam + struct.calcsize(fmt))
    else:
        raise NotImplementedError("unknown device type %d" % (devtype,))
    return win32gui_struct.DEV_BROADCAST_INFO(devtype, **extra)

win32gui_struct.UnpackDEV_BROADCAST = _UnpackDEV_BROADCAST

class PySvc(win32serviceutil.ServiceFramework):
    # writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into Class PySvc"))

    # you can NET START/STOP the service by the following name
    _svc_name_ = ServiceName
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = ServiceDisplayName
    # this text shows up as the description in the SCM
    _svc_description_ = ServiceDescription

    def __init__(self, args):
        module.Module(module=module.ModuleEnum.Deamon)
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into __init__"))

        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        # Creates a waitable event
        self.evStop = win32event.CreateEvent(None, 0, 0, None)
        self.evPause = win32event.CreateEvent(None, 0, 0, None)
        self.evContinue = win32event.CreateEvent(None, 0, 0, None)
        self.evShutdown = win32event.CreateEvent(None, 0, 0, None)

        self.daemon = Daemon.Daemon()
        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
            GUID_DEVINTERFACE_USB_DEVICE)
        self.hdn = win32gui.RegisterDeviceNotification(self.ssh, filter,
                                                       win32con.DEVICE_NOTIFY_SERVICE_HANDLE)

    # Override the base class so we can accept additional events.
    # if you need to handle controls via SvcOther[Ex](), you must override this.
    def GetAcceptedControls(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into GetAcceptedControls"))

        # say we accept them all.
        rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)

        writeDebugMsg("[{0}]: rc1= {1}".format(str(datetime.datetime.now()), str(rc)))
        rc |= win32service.SERVICE_ACCEPT_PARAMCHANGE \
              | win32service.SERVICE_ACCEPT_NETBINDCHANGE \
              | win32service.SERVICE_CONTROL_DEVICEEVENT \
              | win32service.SERVICE_ACCEPT_HARDWAREPROFILECHANGE \
              | win32service.SERVICE_ACCEPT_POWEREVENT \
              | win32service.SERVICE_ACCEPT_SESSIONCHANGE \
              | win32service.SERVICE_ACCEPT_PRESHUTDOWN

        #  Note that services that register for SERVICE_CONTROL_PRESHUTDOWN notifications
        #  cannot receive SERVICE_CONTROL_SHUTDOWN notification because they have already stopped.

        writeDebugMsg("[{0}]: rc2= {1}".format(str(datetime.datetime.now()), str(rc)))
        # rc: dec to bin, check dwControlsAccepted flag raised.
        # ref: https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/4e91ff36-ab5f-49ed-a43d-a308e72b0b3c
        return rc

    def SvcDoRun(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcDoRun"))
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )  # Logs a specific message

        rc = None
        # if the stop event hasn't been fired keep looping
        while rc != win32event.WAIT_OBJECT_0:
            try:
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcDoRun"))
                self.daemon.start()
            except Exception:
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STOPPED,
                    (self._svc_name_, 'Exception')
                )
                # traceback.print_exc(file=f)

    # called when we're being shut down
    def SvcStop(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcStop"))

        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=10000)
        # fire the stop event
        win32event.SetEvent(self.hWaitStop)
        self.daemon.stop()
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ' :SvcStop')
        )

    # servicemanager registers ServiceCtrlHandlerEx function to retrieve service control notification messages.
    # ServiceCtrlHandlerEx also invoke SvcOtherEx()
    # All extra events are sent via SvcOtherEx
    def SvcOtherEx(self, control, event_type, data):

        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcOtherEx"))
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(control)))
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(event_type)))
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(data)))

        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:   # a change to the hardware configuration of a device or the computer.
          writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "SERVICE_CONTROL_DEVICEEVENT"))

          info = win32gui_struct.UnpackDEV_BROADCAST(data)
          #
          # This is the key bit here where you'll presumably
          # do something other than log the event. Perhaps pulse
          # a named event or write to a secure pipe etc. etc.
          #

          if event_type == DBT_DEVICEARRIVAL:  # A device or piece of media has been inserted and is now available.
            try:
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "DBT_DEVICEARRIVAL"))
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(info.name)))

                self.daemon.deviceChanged(event_type, data, info.name)
            except Exception:
                writeDebugMsg(
                    "[{0}]: {1}".format(str(datetime.datetime.now()), str(traceback.format_exc().encode('UTF-8'))))

                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    0xF000,
                    ('start daemon failure')
                )

          elif event_type == DBT_DEVICEREMOVECOMPLETE:  # A device or piece of media has been removed.

            try:
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "DBT_DEVICEREMOVECOMPLETE"))
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(info.name)))

                self.daemon.deviceChanged(event_type, data, info.name)
            except Exception:
                writeDebugMsg(
                    "[{0}]: {1}".format(str(datetime.datetime.now()), str(traceback.format_exc().encode('UTF-8'))))

                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    0xF000,
                    ('stop daemon failure')
                )

        elif control == win32service.SERVICE_CONTROL_PRESHUTDOWN: #  service that handles this notification blocks system shutdown until the service stops
            writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "SERVICE_CONTROL_PRESHUTDOWN"))

            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=10000)  # Giving windows Service more time to stop, waitHint unit: ms
            self.daemon.stop()
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STOPPED, (self._svc_name_, ' :SvcOtherEx CONTROL_PRESHUTDOWN'))

        elif control == win32service.SERVICE_CONTROL_POWEREVENT: # power-management event has occurred.
            writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "SERVICE_CONTROL_POWEREVENT"))

            if event_type == PBT_APMSUSPEND:  # 4 (0x4): System is suspending operation (Windows Sleep/Hibernate)
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "PBT_APMSUSPEND"))

                self.daemon.hibernate()

            if event_type == PBT_APMRESUMEAUTOMATIC:  # 18 (0x12): the system resumes
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "PBT_APMRESUMEAUTOMATIC"))

                self.daemon.hibernateResume()

        elif control == win32service.SERVICE_CONTROL_SESSIONCHANGE:
            writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "SERVICE_CONTROL_SESSIONCHANGE"))

            if event_type == WTS_SESSION_LOGON:  # 5(0x5): user has logged on
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "WTS_SESSION_LOGON"))

                # write your code here

            elif event_type == WTS_SESSION_LOGOFF:  # 6(0x6): user has logged off
                writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "WTS_SESSION_LOGOFF"))

                # write your code here

    def SvcPause(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcPause"))

        self.ReportServiceStatus(win32service.SERVICE_PAUSE_PENDING) # Sets the current service status and reports it to the SCM.
        win32event.SetEvent(self.evPause) # Sets an event

    def SvcContinue(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcContinue"))

        self.ReportServiceStatus(win32service.SERVICE_CONTINUE_PENDING) # Sets the current service status and reports it to the SCM.
        # win32event.SetEvent(self.evContinue) # Sets an event

    def SvcShutdown(self):
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into SvcShutdown"))

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.daemon.stop()
        win32event.SetEvent(self.evShutdown) # Sets an event
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STOPPED,(self._svc_name_, ' :SvcShutdown'))


if __name__ == '__main__':
    # import sys

    delDebugFile()  # remove previous file
    writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into __main__"))

    try:
        "Windows service installed"
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into Windows service installed"))

        win32serviceutil.QueryServiceStatus(ServiceName) # Retrieves the current status of the specified service. Type: SERVICE_STATUS structure
    except:  # into block when first installed
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into InstallService"))
        win32serviceutil.InstallService(
            "WinService.PySvc",
            ServiceName,
            ServiceDisplayName,
            description=ServiceDescription,
            startType=win32service.SERVICE_AUTO_START,
            # delayedstart=True
        )
    servicemanager.Initialize()  # Initialize the module for hosting a service.
    servicemanager.PrepareToHostSingle(PySvc)  # Prepare for hosting a single service in this EXE
    try:
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), "Into StartServiceCtrlDispatcher"))
        servicemanager.StartServiceCtrlDispatcher() # Starts the service by calling the win32 StartServiceCtrlDispatcher function.
    except Exception:
        writeDebugMsg("[{0}]: {1}".format(str(datetime.datetime.now()), str(traceback.format_exc().encode('UTF-8'))))