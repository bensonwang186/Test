import sys
import traceback

import views.MainPages.About as aboutView
from System import systemDefine
from Utility import Logger


class DeviceStatusHandler:
    def __init__(self, masterPage, client, daemonStatus, tray):
        self.daemonStatus = daemonStatus
        self.masterPage = masterPage
        self.client = client
        self.tray = tray

        self.client.deviceStatusUpdateSignal.connect(self.deviceStatusUpdate)
        self.client.deviceStatusUpdateSignal.connect(self.tray.changeTrayStatus)
        self.daemonStatus.daemonStatusUpdateSignal.connect(self.tray.setTrayNotReadyStatus)
        self.daemonStatus.daemonStatusUpdateSignal.connect(self.overviewStatusUpdate)

    def overviewStatusUpdate(self, daemonStatus):
        Logger.LogIns().logger.info("over view status update")
        # update status and side bar
        self.masterPage.overviewStatusUpdate(daemonStatus)
        Logger.LogIns().logger.info("update side bar")
        self.masterPage.updateNoDaemonSideBar()

        # update views
        Logger.LogIns().logger.info("update current status page")
        self.masterPage.updateCurrentStatusPage(None)
        Logger.LogIns().logger.info("update energy reporting page")
        self.masterPage.energyReportingPage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update schedule page")
        self.masterPage.schedulePage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update notification page")
        self.masterPage.notificationPage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update runtime page")
        self.masterPage.runtimePage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update self test page")
        self.masterPage.selfTestPage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update advanced page")
        self.masterPage.advancedPage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update summary page")
        self.masterPage.summaryPage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update voltage page")
        self.masterPage.voltagePage.updatePageByStatus(daemonStatus)
        Logger.LogIns().logger.info("update event log page")
        self.masterPage.eventLogsPage.updatePageByStatus(daemonStatus)

    def deviceStatusUpdate(self, deviceStatus):
        try:
            if deviceStatus.deviceId != self.daemonStatus.deviceId:
                if deviceStatus.deviceId != -1:
                    self.daemonStatus.deviceId = deviceStatus.deviceId
                    self.daemonStatus.daemonStatusUpdateSignal.emit(self.daemonStatus)
                else:
                    self.daemonStatus.deviceId = -1
                    self.daemonStatus.daemonStatusUpdateSignal.emit(self.daemonStatus)

                    # 當device id = -1時，將about頁面資訊設為unknow, configure ups alarm disabled
                    updateData = aboutView.About().DisplayData()
                    self.masterPage.updateAboutPage(updateData)
                    self.masterPage.disableConfigure()

            self.masterPage.updateStatusSideBar(deviceStatus)
            self.masterPage.updateCurrentStatusPage(deviceStatus)
            self.masterPage.voltagePage.updateCurrentVoltage(deviceStatus)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
