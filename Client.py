import logging
import os, platform
import sys

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QDesktopWidget

from ClientHandler import DeviceStatusHandler, NotificationHandler, DevicePropHandler, \
    RuntimeHandler, DeviceConfigHandler, ScheduleHandler, VoltageHandler, AdvancedHandler, EnergyHandler, \
    SelfTestHandler, SummaryHandler, AppTrayHandler, MenuHandler, EventLogsHandler
from ClientHandler.SoftwareUpdateHandler import SoftwareUpdateHandler
from ClientModel import DaemonStatus
from System import settings, module
from i18n import appLocaleData
from major import AppClient
from views import (MasterPage)
from views.TrayMenu import AppTray
from Utility import Logger

# import qt resourse file for Mac
if platform.system() == 'Darwin':
    import resources.qt_resources

class AppMonitor(QObject):
    def __init__(self):
        pass

    def stop(self, app):
        app.exit(0)


class PPApplication(QApplication):
    def __init__(self, argv):
        super(PPApplication, self).__init__(argv)
        self.isFirst = True

    def closeEvent(self):
        # Let the Exit button handle tab closing
        print("close event captured. Do nothing.")

        # Alternatively, if you want to EXIT the application when the close event
        # occurs,  you can implement that code  here!

    def activeEvent(self, state):
        print("Application active event captured. state:" + str(state))
        if state == Qt.ApplicationActive:
            # first time, don't show the masterPage
            if self.isFirst:
                self.isFirst = False
            else:
                masterPage.show()
                # show normal(restore) after it has been minimized
                masterPage.showNormal()


def appExit(signum, frame):
    appTray.hide()
    sys.exit(0)

if __name__ == '__main__':
    module.Module(module=module.ModuleEnum.Client)
    Logger.LogIns().logger.info("*** Client  Start***")
    import signal
    signal.signal(signal.SIGABRT, appExit)
    signal.signal(signal.SIGTERM, appExit)
    signal.signal(signal.SIGINT, appExit)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        )
    logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

    import platform
    if platform.system() == 'Windows':
        import ctypes

        # set a app id for show task bar icon on windows
        myappid = 'cyberpower.systems.pppe'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    import io

    # 讀取檔案中的紀錄初始化Client語系
    locale = appLocaleData.appLocaleData.en_US

    with open(settings.langSetting, mode='rb') as file:
        for line in file:
            io.BytesIO(line)
            locale = line.decode("utf-8", errors='ignore')
            # print(len(locale))

    appLocaleData.appLocaleRecorder().appLocale = locale

    # device = Device.Device()
    appMonitor = AppMonitor()
    app = PPApplication(sys.argv)  # 新增一個Qt應用程式，管理所有的Qt物件資源並且傳入sys.argv作為初始化資料
    appIconPath = os.path.join(settings.IMAGE_PATH, "pppe256.png")
    appIcon = QIcon(appIconPath)
    app.setWindowIcon(appIcon)
    app.aboutToQuit.connect(app.closeEvent)
    app.applicationStateChanged.connect(app.activeEvent)
    daemonStatus = DaemonStatus.DaemonStatus()

    client = AppClient.Client(daemonStatus)

    trayIconPath = os.path.join(settings.IMAGE_PATH, "warning.ico")
    trayIcon = QIcon(trayIconPath)


    masterPage = MasterPage.MasterPage()
    masterPage.setWindowFlags(masterPage.windowFlags() | Qt.FramelessWindowHint | Qt.Window)

    appTray = AppTray.AppTray(trayIcon, masterPage, daemonStatus)

    deviceStatusHandler = DeviceStatusHandler.DeviceStatusHandler(masterPage, client, daemonStatus, appTray)
    notificationHanlder = NotificationHandler.NotifycationHandler(masterPage.notificationPage, client, daemonStatus, appTray)
    devicePropHandler = DevicePropHandler.DevicePropHandler(masterPage, client, daemonStatus)
    summaryHandler = SummaryHandler.SummaryHandler(masterPage.summaryPage, client, daemonStatus, appTray)
    runtimeHandler = RuntimeHandler.RuntimeHandler(masterPage.runtimePage, client, daemonStatus, appTray)
    deviceConfigHandler = DeviceConfigHandler.DeviceConfigHandler(masterPage.notificationPage, client, appTray)
    scheduleHandler = ScheduleHandler.ScheduleHandler(masterPage.schedulePage, client)
    voltageHandler = VoltageHandler.VoltageHandler(masterPage.voltagePage, client)
    advancedHandler = AdvancedHandler.AdvancedHandler(masterPage.advancedPage, client, appTray)
    energyHandler = EnergyHandler.EnergyHandler(masterPage.energySettingsPage, masterPage.energyReportingPage, client)
    selfTestHandler = SelfTestHandler.SelfTestHandler(masterPage.selfTestPage, client, daemonStatus)
    appTrayHandler = AppTrayHandler.AppTrayHandler(appTray, client, daemonStatus)
    menuHandler = MenuHandler.MenuHandler(masterPage, client, daemonStatus)
    eventLogsHandler = EventLogsHandler.EventLogsHandler(masterPage.eventLogsPage, client, daemonStatus, appTray)
    software_update_handler = SoftwareUpdateHandler(masterPage.aboutPage, client)

    appTray.show()

    dw = QDesktopWidget()  # The QDesktopWidget class provides access to screen information on multi-head systems.
    dw.setObjectName("mainWindow")
    masterPage.setFixedSize(860, 710)  # fixed size

    """load fonts(需在load qss之前, 以避免qss讀不到字型)"""
    # 2019/02/23 Kenneth Setting fonts bold
    fonts = os.path.join(settings.FONT_PATH, "Roboto-Regular.ttf", "Roboto-Bold.ttf")
    # # fontsBold = os.path.join(settings.FONT_PATH, "Roboto-Bold.ttf")
    QFontDatabase.addApplicationFont(os.path.join(settings.FONT_PATH, "Roboto-Regular.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(settings.FONT_PATH, "Roboto-Bold.ttf"))

    # # QFontDatabase.addApplicationFont(fontsBold)

    """load qss"""
    style_file = "style_win.qss"

    if platform.system() == 'Windows':
        style_file = "style_win.qss"
    elif platform.system() == 'Darwin':
        style_file = "style_mac.qss"
    mainStyle = os.path.join(settings.STYLESHEET_PATH, style_file)
    masterPage.setStyleSheet(open(mainStyle, "r").read())  # setting qss

    # masterPage.show()
    if (platform.system() == "Windows"):
        if (sys.argv.__len__() >= 2):
            if (sys.argv[1] == "first"):
                masterPage.show()
    elif platform.system() == "Darwin":
        if sys.argv.__len__() >= 2:
            if sys.argv[1] == "first":
                masterPage.show()
        elif 'first' == str(os.getenv('argv')):
            masterPage.show()
        else:
            command = 'launchctl setenv argv first'
            os.system(command)

    sys.exit(app.exec_())
