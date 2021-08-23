import os
import sys
import traceback

from PyQt5 import QtGui

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

from System import settings, systemDefine
from Utility import i18nTranslater
from PyQt5.QtCore import QTimer, Qt

import platform
if platform.system() == 'Windows':
    import winsound
elif platform.system() == 'Darwin':
    import soundfile
    import sounddevice

from i18n import i18nId, appLocaleData
from views.MainPages import TemplatePage
from i18n.appLocaleData import appLocaleRecorder
from Utility import Logger
NOSOUND = 0
SOUND = 1

class AppTray(QSystemTrayIcon, TemplatePage.TemplatePage):
    mesgDelayTime = 3000

    _setlocaleSignal = pyqtSignal(object)

    @property
    def setlocaleSignal(self):
        return self._setlocaleSignal

    @setlocaleSignal.setter
    def setlocaleSignal(self, value):
        self._setlocaleSignal = value

    def __init__(self, icon, dialog, daemonStatus, parent=None):

        self.initFlag = True
        self.shutdownMsgTimer = None
        self.shutdownType = 0
        self.softwareSoundEnable = 0
        self.passed = 0
        self.daemonStatus = daemonStatus
        self.deviceStatus = None
        self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorder().appLocale)
        self.onBatteryPowerTitle = self.i18nTranslater.getTranslateString(
            i18nId.i18nId().UPS_no_longer_receiving_AC_utility_power)
        self.onBatteryPowerMsg = self.i18nTranslater.getTranslateString(
            i18nId.i18nId().Your_UPS_is_now_supplying_battery_power_to_your_equipment)
        QSystemTrayIcon.__init__(self, icon, parent)

        self.masterPage = dialog
        self.menu = QMenu(parent)

        self.menu.setAccessibleName("traymenu")

        self.openAction1 = QAction("Open", self)
        self.openAction1.triggered.connect(self.openApp)
        self.menu.addAction(self.openAction1)

        self.menu.addSeparator()

        self.openAction2 = QAction("Status", self)
        self.openAction2.triggered.connect(self.openStatus)
        self.menu.addAction(self.openAction2)

        self.openAction3 = QAction("Summary", self)
        self.openAction3.triggered.connect(self.openSummary)
        self.menu.addAction(self.openAction3)

        self.openAction4 = QAction("Configure", self)
        self.openAction4.triggered.connect(self.openConfiguration)
        self.menu.addAction(self.openAction4)

        self.menu.addSeparator()

        # about action
        self.languageMenu = QMenu(parent)
        self.languageMenu.setTitle("Change Language")

        # action1 = QAction("Change Language", self)
        # self.menu.addAction(action1)

        action2 = QAction("簡體中文(Simplified Chinese)", self)
        action3 = QAction("繁體中文(Traditional Chinese)", self)
        action4 = QAction("čeština(Czech)", self)
        action5 = QAction("English(English)", self)
        action6 = QAction("français(French)", self)
        action7 = QAction("Deutsch(German)", self)
        # action8 = QAction("Magyer (Hungarian)", self)
        # action9 = QAction("Italiano(Italian)", self)
        action10 = QAction("日本語(Japanese)", self)
        action11 = QAction("Polski(Polish)", self)
        action12 = QAction("Русский(Russian)", self)
        # action13 = QAction("Slovenščina(Slovenian)", self)
        action14 = QAction("Español(Spanish)", self)
        # aboutAction.triggered.connect(self.about_fun)
        # self.languageMenu.addAction(action1)
        self.languageMenu.addAction(action2)
        self.languageMenu.addAction(action3)
        self.languageMenu.addAction(action4)
        self.languageMenu.addAction(action5)
        self.languageMenu.addAction(action6)
        self.languageMenu.addAction(action7)
        # self.languageMenu.addAction(action8)
        # self.languageMenu.addAction(action9)
        self.languageMenu.addAction(action10)
        self.languageMenu.addAction(action11)
        self.languageMenu.addAction(action12)
        # self.languageMenu.addAction(action13)
        self.languageMenu.addAction(action14)
        action2.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().zh_CN))
        action3.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().zh_TW))
        action4.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().cs_CZ))
        action5.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().en_US))
        action6.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().fr_FR))
        action7.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().de_DE))
        # action8.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().hu_HU))
        # action9.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().it_IT))
        action10.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().ja_JP))
        action11.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().pl))
        action12.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().ru))
        # action13.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().sl))
        action14.triggered.connect(lambda: self.changeLanguage(appLocaleData.appLocaleData().es_ES))

        self.menu.addMenu(self.languageMenu)

        # language action
        # i18nTranslater.getTranslateString(i18nId.i18nId())
        # quitAction = QAction("Quit", self)
        # quitAction.triggered.connect(self.quit_fun)
        # self.menu.addAction(quitAction)

        # status flag
        self.isUtilityPowerFailure = False
        self.isCommunicationLost = True

        # image
        self.normalIconPath = os.path.join(settings.IMAGE_PATH, "normal.ico")
        self.warningIconPath = os.path.join(settings.IMAGE_PATH, "warning.ico")
        self.batteryIconPath = os.path.join(settings.IMAGE_PATH, "battery.ico")
        self.setContextMenu(self.menu)

        # listen activated
        self.activated.connect(self.iconActivated)

        self.setInitLanguage(appLocaleData.appLocaleRecorder().appLocale)

    def openStatus(self):
        try:
            self.openApp()
            self.masterPage.mainPageSwitch(self.masterPage.monitorBtn)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def openSummary(self):
        try:
            self.openApp()
            self.masterPage.mainPageSwitch(self.masterPage.monitorBtn)
            for listWidget in self.masterPage.tapStackedWidget.children():
                if listWidget.property('name') == systemDefine.PAGE_MONITOR:
                    listWidget.setCurrentRow(1)
            print(len(self.masterPage.tapStackedWidget.children()))
            self.masterPage.pagesWidget.setCurrentIndex(1)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def openConfiguration(self):
        try:
            self.openApp()
            self.masterPage.mainPageSwitch(self.masterPage.configBtn)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def openApp(self):
        self.masterPage.setWindowState(Qt.WindowNoState)
        if self.masterPage.isHidden():
            self.masterPage.setHidden(False)
        self.masterPage.raise_()
    def about_fun(self):
        QtGui.QMessageBox.about(self.parent(), "about", "pyqt system tray")

    def quit_fun(self):
        sys.exit(0)

    def setTrayNotReadyStatus(self, daemonStatus):
        try:
            self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleRecorder().appLocale)

            unableCommunicateTitle = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Unable_to_communicate_with_UPS)
            unableCommunicateMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Please_make_sure_the_USB_or_serial_cable_is_connected_between_the_UPS_and_computer)
            communicateRestoreTitleMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Communication_with_UPS_is_restored)
            communicateRestoreMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Your_UPS_is_correctly_connected_to_your_computer)

            serviceOffMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().application_full_name_Service_is_not_running)
            if daemonStatus:
                Logger.LogIns().logger.info("if daemonStatus:")
                if daemonStatus.isDaemonStarted:
                    Logger.LogIns().logger.info("if daemonStatus.isDaemonStarted:")
                    trayIconPath = self.warningIconPath
                    self.setToolTip(unableCommunicateTitle)
                    # self.showMesg(NOSOUND, unableCommunicateTitle, unableCommunicateMsg, QSystemTrayIcon.Critical)
                elif not daemonStatus.isDaemonStarted:
                    Logger.LogIns().logger.info("elif not daemonStatus.isDaemonStarted:")
                    trayIconPath = self.warningIconPath
                    self.setToolTip(serviceOffMsg)
                    self.showMesg(NOSOUND, serviceOffMsg, serviceOffMsg, QSystemTrayIcon.Critical)
                    self.isCommunicationLost = True
                    self.stopShutdownMsgTimer()
                if trayIconPath:
                    trayIcon = QIcon(trayIconPath)
                    self.setIcon(trayIcon)
        except Exception:
            Logger.LogIns().logger.info(traceback.format_exc())

    def processShutdownStatus(self, type, total):
        self.shutdownMsgTimer = QTimer()
        # total = remain*60
        self.shutdownMsgTimer.timeout.connect(lambda: self.changeShutdownMsg(type, total))
        self.shutdownMsgTimer.start(60000)  # msecs
        self.changeShutdownMsg(type, total)

    def showMesg(self, msgLevel, title, msg, icon):
        if msgLevel == SOUND and self.softwareSoundEnable:
            if platform.system() == 'Windows':
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            elif platform.system() == 'Darwin':
                macAudioFile = '/System/Library/Sounds/Glass.aiff'
                if os.path.isfile(macAudioFile):
                    data, fs = soundfile.read(macAudioFile)
                    sounddevice.play(data, fs, blocking=True)
        self.showMessage(title, msg, icon, msecs=self.mesgDelayTime)

    def changeShutdownMsg(self, type, total):

        current = 0
        # action = "shut down"
        action = "shut down"
        if self.shutdownType == 1:
            action = "hibernate"
        if type == 0:
            # first int is remove float point
            # second int is converted RemainingRuntime
            # current = int(int(self.deviceStatus.RemainingRuntime)/60) - total
            timeSec = float(self.deviceStatus.RemainingRuntime) - float(total * 60)
            current = round(timeSec / 60)

        elif type == 1:
            current = total - self.passed

        msg = ""
        self.onBatteryPowerTitle = self.i18nTranslater.getTranslateString(
            i18nId.i18nId().UPS_no_longer_receiving_AC_utility_power)
        self.onBatteryPowerMsg = self.i18nTranslater.getTranslateString(
            i18nId.i18nId().Your_UPS_is_now_supplying_battery_power_to_your_equipment)

        commaStr = ", "
        if current <= 0:
            if action is "shut down":
                msg = self.i18nTranslater.getTranslateString(i18nId.i18nId().Your_computer_will_be_shutdown_immediately)
            elif action is "hibernate":
                msg = self.i18nTranslater.getTranslateString(
                    i18nId.i18nId().Your_computer_will_enter_hibernate_immediately)

            self.setToolTip(msg)

            if appLocaleRecorder().appLocale == appLocaleData.appLocaleData().ja_JP:
                commaStr = ""

            self.showMesg(SOUND, self.onBatteryPowerTitle, (self.onBatteryPowerMsg + commaStr + msg),
                          QSystemTrayIcon.Critical)
        else:
            if action is "shut down":
                msg = self.i18nTranslater.getTranslateString(
                    i18nId.i18nId().Your_computer_will_be_shutdown_in_xxxx_seconds).replace("xxxx", str(current))
            elif action is "hibernate":
                msg = self.i18nTranslater.getTranslateString(
                    i18nId.i18nId().Your_computer_will_enter_hibernate_in_xxxx_seconds).replace("xxxx", str(current))

            self.setToolTip(msg)

            if appLocaleRecorder().appLocale == appLocaleData.appLocaleData().ja_JP:
                commaStr = ""

            self.showMesg(SOUND, self.onBatteryPowerTitle, (self.onBatteryPowerMsg + commaStr + msg),
                          QSystemTrayIcon.Critical)

        self.passed += 1

    def configChange(self, type, total):
        if self.shutdownMsgTimer is not None:
            self.shutdownMsgTimer.stop()
            self.passed = 0
            self.processShutdownStatus(type, total)

    def changeTrayStatus(self, deviceStatus):
        Logger.LogIns().logger.info("[Client] trail receive status, status update")
        self.deviceStatus = deviceStatus
        try:
            unableCommunicateTitle = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Unable_to_communicate_with_UPS)
            unableCommunicateMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Please_make_sure_the_USB_or_serial_cable_is_connected_between_the_UPS_and_computer)
            communicateRestoreTitleMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Communication_with_UPS_is_restored)
            communicateRestoreMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Your_UPS_is_correctly_connected_to_your_computer)

            powerRestoreTtile = self.i18nTranslater.getTranslateString(i18nId.i18nId().Utility_power_restored_to_UPS)
            powerRestoreMsg = self.i18nTranslater.getTranslateString(
                i18nId.i18nId().Your_equipment_is_now_running_on_AC_utility_power)
            powerpanelTitle = "CyberPower PowerPanel Personal"


            if not deviceStatus:
                pass
            elif not self.isCommunicationLost and deviceStatus.deviceId == -1:  # communicate lost
                self.stopShutdownMsgTimer()
                self.isCommunicationLost = True
                self.setToolTip(unableCommunicateTitle)
                self.showMesg(NOSOUND, unableCommunicateTitle, unableCommunicateMsg, QSystemTrayIcon.Critical)
            elif self.isCommunicationLost and deviceStatus.deviceId != -1:  # communicate restore
                if self.isUtilityPowerFailure:
                    self.stopShutdownMsgTimer()
                self.isCommunicationLost = False
                self.isUtilityPowerFailure = False
                self.setToolTip(powerpanelTitle)
                self.showMesg(NOSOUND, communicateRestoreTitleMsg, communicateRestoreMsg, QSystemTrayIcon.Information)
            elif not self.isUtilityPowerFailure and deviceStatus.UtilityPowerFailure:  # occur power failure
                # print("********deviceStatus.SelfTestFWErrFlag: " + str(deviceStatus.SelfTestFWErrFlag))
                if deviceStatus.SelfTestFWErrFlag:
                    self.isUtilityPowerFailure = True
                    self.setToolTip(self.onBatteryPowerMsg)
                    self.processShutdownStatus(self.daemonStatus.shutdownType, self.daemonStatus.shutdownTime)
            elif self.isUtilityPowerFailure and deviceStatus.deviceId != -1 and not deviceStatus.UtilityPowerFailure:  # power failure restore

                self.stopShutdownMsgTimer()
                powerRestoreMsg = powerRestoreMsg + ", " + self.i18nTranslater.getTranslateString(
                    i18nId.i18nId().the_shutdown_process_has_been_aborted)
                self.isUtilityPowerFailure = False
                self.setToolTip(powerpanelTitle)
                self.showMesg(NOSOUND, powerRestoreTtile, powerRestoreMsg, QSystemTrayIcon.Information)
            self.decideTrayIcon(deviceStatus)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def decideTrayIcon(self, deviceStatus):
        trayIconPath = None

        if deviceStatus.UtilityPowerFailure:  # still power failure
            if deviceStatus.SelfTestFWErrFlag:
                trayIconPath = self.batteryIconPath
        elif not deviceStatus.UtilityPowerFailure:  # still power failure
            trayIconPath = self.normalIconPath

        # bug fix 有時候 通訊回復時icon不會回復成綠色的icon，因icon跟tooltip不一樣，應不用針對lost或restore當下做出一次性的顯示
        # 所以改成每次都檢查device id來決定icon的樣式
        if deviceStatus.deviceId == -1:
            trayIconPath = self.warningIconPath

        if trayIconPath:
            trayIcon = QIcon(trayIconPath)
            self.setIcon(trayIcon)
            Logger.LogIns().logger.info("[Client] trail receive status, status update done")

    def stopShutdownMsgTimer(self):
        try:
            if self.shutdownMsgTimer is not None:
                self.shutdownMsgTimer.stop()
                self.shutdownMsgTimer = None
                self.passed = 0
            else:
                self.passed = 0
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            try:
                # self.masterPage.showNormal() # for windows minimize
                # self.masterPage.show()  # for windows hide
                self.openApp()
            except Exception:
                traceback.print_exc(file=sys.stdout)

    def changeLanguage(self, localeStr):
        appLocaleRecorder().appLocale = localeStr
        self.i18nTranslater = i18nTranslater.i18nTranslater(localeStr)
        self.masterPage.reRender(localeStr)

        self.openAction1.setText(self.getTranslateString(i18nId.i18nId().Open))
        self.openAction2.setText(self.getTranslateString(i18nId.i18nId().Status))
        self.openAction3.setText(self.getTranslateString(i18nId.i18nId().Summary))
        self.openAction4.setText(self.getTranslateString(i18nId.i18nId().Configure))
        self.languageMenu.setTitle(self.getTranslateString(i18nId.i18nId().Change_Language))

        try:
            self._setlocaleSignal.emit(localeStr)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def setInitLanguage(self, localeStr):
        appLocaleRecorder().appLocale = localeStr
        self.i18nTranslater = i18nTranslater.i18nTranslater(localeStr)
        self.masterPage.reRender(localeStr)

        self.openAction1.setText(self.getTranslateString(i18nId.i18nId().Open))
        self.openAction2.setText(self.getTranslateString(i18nId.i18nId().Status))
        self.openAction3.setText(self.getTranslateString(i18nId.i18nId().Summary))
        self.openAction4.setText(self.getTranslateString(i18nId.i18nId().Configure))
        self.languageMenu.setTitle(self.getTranslateString(i18nId.i18nId().Change_Language))

        self.initFlag = False
