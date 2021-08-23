import os
import traceback

import sys
import platform
from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot, QTranslator
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QListView, QListWidget, QListWidgetItem, QStackedWidget, QVBoxLayout,
                             QLabel, QPushButton, QWidget, QSizePolicy, QApplication)

import model_Json
import views.Custom.ViewData
from ClientModel import DaemonStatus
from System import settings, systemDefine, systemFunction
from Utility import i18nTranslater, Logger
from i18n import i18nId, appLocaleData
from views.MainPages import (CurrentStatus, About, Summary, Schedule, Notification, Runtime,
                             Voltage, SelfTest, Advanced, EnergySettings, EnergyReporting, ConfigrationMain, EventLogs)


class CustomTitleButton(QPushButton):
    """
    """
    purpose = "ND"
    pressed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomTitleButton, self).__init__(parent)

    def setPurpose(self, purpose):
        self.purpose = purpose

    def mousePressEvent(self, event):
        self.setDown(True)
        self.pressed_signal.emit(self.purpose)

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.setDown(False)

    def enterEvent(self, event):
        self.setStyleSheet("background-color:#333333;max-width:30px;height:40px;")
        self.setCursor(Qt.ArrowCursor)

    def leaveEvent(self, event):
        self.setStyleSheet("background-color:#2B2B2B;max-width:30px;height:40px;")

class CustomTitleWidget(QWidget):
    """
    """

    __x_pressed = 0
    __y_pressed = 0
    __global_x_pressed = 0
    __global_y_pressed = 0
    __up_left_x = 0
    __up_left_y = 0
    position_change = pyqtSignal(int, int, name='positionRefChanged')
    close_minify_pressed = pyqtSignal(str, name='closeMinifyPressed')

    def __init__(self, parent=None):
        super(CustomTitleWidget, self).__init__(parent)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        title_label = QLabel(' ', self)
        title_label.setAccessibleName("appnamelabel")
        title_label.setProperty('class', 'title_label')

        hbox.addWidget(title_label)

        edition_label = QLabel(' ', self)
        edition_label.setAccessibleName("editionlabel")
        edition_label.setProperty('class', 'edition_label')
        hbox.addWidget(edition_label)

        space_label = QLabel('', self)
        space_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hbox.addWidget(space_label)

        if platform.system() == 'Darwin':
            # QTBUG-64994, it can not handle showMinimized() well, and caused window display failure.
            # Do not present minimize button on MacOS
            pass
        else:
            p_minimize = CustomTitleButton(" ")
            p_minimize.setAccessibleName("minifybtn")
            p_minimize.setPurpose("minimize")
            p_minimize.pressed_signal.connect(self.triggerBaseWidgetAction)

            # p_minimize.setStyleSheet("background-color:#2B2B2B;width:40px;height:40px")
            p_minimize.setProperty('class', 'p_minimize')
            hbox.addWidget(p_minimize, 0, Qt.AlignLeft)

        p_hide = CustomTitleButton(" ")
        p_hide.setAccessibleName("hidebtn")
        p_hide.setPurpose("hide")
        p_hide.pressed_signal.connect(self.triggerBaseWidgetAction)

        # p_hide.setStyleSheet("background-color:#2B2B2B;width:40px;height:40px")
        p_hide.setProperty('class', 'p_hide')
        hbox.addWidget(p_hide, 0, Qt.AlignLeft)

        self.setLayout(hbox)
        title_label.show()
        edition_label.show()
        if platform.system() == 'Darwin':
            pass
        else:
            p_minimize.show()
        p_hide.show()

    @pyqtSlot(str)
    def triggerBaseWidgetAction(self, purpose):
        self.close_minify_pressed.emit(purpose)

    def mousePressEvent(self, event):
        # self.setCursor(Qt.ClosedHandCursor)
        self.__x_pressed = event.pos().x()
        self.__y_pressed = event.pos().y()
        global_x_pressed = event.globalX()
        global_y_pressed = event.globalY()
        self.__up_left_x = global_x_pressed - self.__x_pressed
        self.__up_left_y = global_y_pressed - self.__y_pressed

    def mouseMoveEvent(self, event):
        x_move = event.pos().x()
        y_move = event.pos().y()
        x_diff = x_move - self.__x_pressed
        y_diff = y_move - self.__y_pressed
        should_move = False
        if (x_diff is not 0) or (y_diff is not 0):
            should_move = True

        x = self.__up_left_x + x_diff
        y = self.__up_left_y + y_diff
        self.__up_left_x = x
        self.__up_left_y = y
        if should_move == True:
            self.position_change.emit(x, y)

    def mouseReleaseEvent(self, event):
        # self.setCursor(Qt.OpenHandCursor)
        x_released = event.pos().x()
        y_released = event.pos().y()
        x_diff = x_released - self.__x_pressed
        y_diff = y_released - self.__y_pressed
        should_move = False
        if (x_diff is not 0) or (y_diff is not 0):
            should_move = True
        x = self.__up_left_x + x_diff
        y = self.__up_left_y + y_diff
        if should_move == True:
            self.position_change.emit(x, y)

    def enterEvent(self, event):
        # self.setCursor(Qt.OpenHandCursor)
        pass

    def leaveEvent(self, event):
        pass


class MasterPage(QDialog):
    def __init__(self, parent=None):
        super(MasterPage, self).__init__(parent,
                                         flags=Qt.MSWindowsFixedSizeDialogHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # self.transactionData = trx
        self.powerSourceLabel = None
        self.capacityLabel = None
        self.runtimeLabel = None
        self.statusListWidgetItem = None
        self.summaryListWidgetItem = None
        self.eventLogsListWidgetItem = None
        self.scheduleListWidgetItem = None
        self.notifyListWidgetItem = None
        self.runtimeListWidgetItem = None
        self.voltageListWidgetItem = None
        self.selfTestListWidgetItem = None
        self.advanceListWidgetItem = None
        self.aboutListWidgetItem = None
        self.energyReportListWidgetItem = None
        self.energySettingListWidgetItem = None

        self.monitorBtn = None
        self.energyBtn = None
        self.configBtn = None
        self.helpBtn = None

        # image init
        # top status
        self.statusNormalImage_top = os.path.join(settings.IMAGE_PATH, "icon_status_normally.png")
        self.statusUnableImage_top = os.path.join(settings.IMAGE_PATH, "icon_status_unable.png")
        self.statusNotReadyImage_top = os.path.join(settings.IMAGE_PATH, "icon_status_not_ready.png")

        # power source
        self.powerSrcNormal = os.path.join(settings.IMAGE_PATH, "icon_power_source.png")
        self.powerSrcBattery = os.path.join(settings.IMAGE_PATH, "icon_power_source_2.png")
        self.powerSrcNoOut = os.path.join(settings.IMAGE_PATH, "icon_power_source_3.png")

        # battery capacity
        self.batteryCapFullImg = os.path.join(settings.IMAGE_PATH, "icon_battery_capacity.png")
        self.batteryCapNoFullImg = os.path.join(settings.IMAGE_PATH, "icon_battery_capacity_2.png")
        self.batteryCapLowImg = os.path.join(settings.IMAGE_PATH, "icon_battery_capacity_3.png")

        # runtime
        self.runTimeNormalImg = os.path.join(settings.IMAGE_PATH, "icon_runtime.png")
        self.runTimeAbnormalImg = os.path.join(settings.IMAGE_PATH, "icon_runtime_2.png")
        self.runTimeDisableImg = os.path.join(settings.IMAGE_PATH, "icon_runtime_3.png")

        self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorder().appLocale)
        self.UI_Init()
        self.deviceId = -1
        self.daemonDown = None  # 目前僅供多語系暫存用
        self.deviceStatus = None  # 目前僅供多語系暫存用
        self.lastTranslator = None

    """設定畫面UI"""

    def UI_Init(self):
        # <editor-fold desc="塞入所有子頁面">

        # <editor-fold desc="頁面實體化">

        self.currentStatusPage = CurrentStatus.CurrentStatus()
        self.aboutPage = About.About()
        self.advancedPage = Advanced.Advanced()
        self.summaryPage = Summary.Summary()
        self.eventLogsPage = EventLogs.EventLogs()
        self.schedulePage = Schedule.Schedule()
        self.notificationPage = Notification.Notification(self)
        self.runtimePage = Runtime.Runtime()
        self.voltagePage = Voltage.Voltage()
        self.selfTestPage = SelfTest.SelfTest()
        self.energySettingsPage = EnergySettings.EnergySettings()
        self.energyReportingPage = EnergyReporting.EnergyReporting()
        self.configrationMainPage = ConfigrationMain.ConfigrationMain(self)

        # </editor-fold>

        self.pagesWidget = QStackedWidget()
        self.pagesWidget.setAccessibleName("pagespane")
        self.pagesWidget.addWidget(self.currentStatusPage)  # 0
        self.pagesWidget.addWidget(self.summaryPage)  # 1
        self.pagesWidget.addWidget(self.eventLogsPage)  # 2
        self.pagesWidget.addWidget(self.energyReportingPage)  # 3
        self.pagesWidget.addWidget(self.energySettingsPage)  # 4
        self.pagesWidget.addWidget(self.configrationMainPage)  # 5
        self.pagesWidget.addWidget(self.schedulePage)  # 6
        self.pagesWidget.addWidget(self.notificationPage)  # 7
        self.pagesWidget.addWidget(self.runtimePage)  # 8
        self.pagesWidget.addWidget(self.voltagePage)  # 9
        self.pagesWidget.addWidget(self.selfTestPage)  # 10
        self.pagesWidget.addWidget(self.advancedPage)  # 11
        self.pagesWidget.addWidget(self.aboutPage)  # 12
        self.pagesWidget.setProperty('class', 'main_contentBox')  # 2017/05/09 Kenneth Add
        self.pagesWidget.setFixedSize(650, 490)
        self.pagesWidget.setContentsMargins(20, 20, 20, 20)

        # </editor-fold>

        # <editor-fold desc="Navi Menu母選單">

        # ---設定Btn QListWidget---
        self.contentsWidget = QListWidget()
        self.contentsWidget.setObjectName("mainBar_btnWidget")
        self.contentsWidget.setFlow(0)  # 設定QListWidget為水平, 1為垂直
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(55, 55))  # 2017/05/09 Kenneth Edit
        # self.contentsWidget.setSpacing(17)  # 2017/05/19 Kenneth Edit
        self.contentsWidget.setMovement(QListView.Static)
        self.contentsWidget.setAccessibleName("contentw")
        self.contentsWidget.setAccessibleDescription("content widget")
        # 2019/02/23 Kenneth Setting default background class
        self.contentsWidget.setProperty('class', 'mainTabCls1')

        # </editor-fold>

        # <editor-fold desc="Status Topbar">

        statusHBox = QHBoxLayout()
        self.statusImage_top = views.Custom.ViewData.ImageWidget(self.statusNotReadyImage_top,
                                                                 "status_imgBox", self)
        self.statusImage_top.setAccessibleName("topstatus")
        Logger.LogIns().logger.info("initial status label")
        self.statusLabel_top = QLabel(
            self.getTranslateString(i18nId.i18nId().PowerPanel_Personal_Edition_Service_is_not_ready))

        self.statusLabel_top.setProperty('class', 'status_TextBox')
        self.statusLabel_top.setWordWrap(True)
        self.statusLabel_top.setFont(QFont("Roboto"))

        statusHBox.addWidget(self.statusImage_top)
        statusHBox.addWidget(self.statusLabel_top)

        # </editor-fold>

        # <editor-fold desc="Navi Menu子選單">

        self.tapStackedWidget = QStackedWidget()
        self.tapStackedWidget.setAccessibleName("pagecontainerpane")
        self.tapStackedWidget.setObjectName("mainBar_pagesWidget")

        naviMenu = views.Custom.ViewData.NaviMenu

        # <editor-fold desc="Monitor子選單">

        self.monitorTabWidget = QListWidget()
        self.monitorTabWidget.setViewMode(QListView.IconMode)
        self.monitorTabWidget.setFlow(0)
        self.monitorTabWidget.setProperty('class', 'tabCls')
        self.monitorTabWidget.setProperty('name', 'monitor')
        self.monitorTabWidget.setFont(QFont("Roboto"))
        # print(self.monitorTabWidget.property('name'))

        self.statusListWidgetItem = mTabItem1 = QListWidgetItem(self.monitorTabWidget)
        mTabItem1.setText("Current Status")
        mTabItem1.setTextAlignment(Qt.AlignHCenter)
        mTabItem1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.summaryListWidgetItem = mTabItem2 = QListWidgetItem(self.monitorTabWidget)
        mTabItem2.setText("Summary")
        mTabItem2.setTextAlignment(Qt.AlignHCenter)
        mTabItem2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.eventLogsListWidgetItem = QListWidgetItem(self.monitorTabWidget)
        self.eventLogsListWidgetItem.setText("Event Logs")
        self.eventLogsListWidgetItem.setTextAlignment(Qt.AlignHCenter)
        self.eventLogsListWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        mLayout = QVBoxLayout()
        mLayout.addWidget(self.monitorTabWidget)
        mLayout.addStretch(1)
        mLayout.setContentsMargins(0, 0, 0, 0)
        mLayout.setSpacing(0)

        self.monitorTabWidget.selectionModel().currentChanged.connect(
            lambda: self.subPageSwitch(naviMenu.Monitor_Module.value))
        self.tapStackedWidget.addWidget(self.monitorTabWidget)

        # </editor-fold>

        # <editor-fold desc="Energy子選單">

        self.energyTabWidget = QListWidget()
        self.energyTabWidget.setViewMode(QListView.IconMode)
        self.energyTabWidget.setFlow(0)  # 設定QListWidget為水平, 1為垂直
        self.energyTabWidget.setProperty('class', 'tabCls')
        self.energyTabWidget.setProperty('name', 'energy')
        self.energyTabWidget.setFont(QFont("Roboto"))

        self.energyReportListWidgetItem = cTabItem1 = QListWidgetItem(self.energyTabWidget)
        cTabItem1.setText("Energy Reporting")
        cTabItem1.setTextAlignment(Qt.AlignHCenter)
        cTabItem1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.energySettingListWidgetItem = cTabItem2 = QListWidgetItem(self.energyTabWidget)
        cTabItem2.setText("Energy Setting")
        cTabItem2.setTextAlignment(Qt.AlignHCenter)
        cTabItem2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        cLayout = QVBoxLayout()
        cLayout.addWidget(self.energyTabWidget)
        cLayout.addStretch(1)

        self.energyTabWidget.selectionModel().currentChanged.connect(
            lambda: self.subPageSwitch(naviMenu.Energy_Module.value))
        self.tapStackedWidget.addWidget(self.energyTabWidget)

        # </editor-fold>

        # <editor-fold desc="Configuration子選單">

        self.configTabWidget = QListWidget()
        self.configTabWidget.setViewMode(QListView.IconMode)
        self.configTabWidget.setFlow(0)
        self.configTabWidget.setProperty('class', 'tabCls')
        self.configTabWidget.setProperty('name', 'config')
        self.configTabWidget.setFont(QFont("Roboto"))

        self.scheduleListWidgetItem = cTabItem1 = QListWidgetItem(self.configTabWidget)
        cTabItem1.setText("Schedule")
        cTabItem1.setTextAlignment(Qt.AlignHCenter)
        cTabItem1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.notifyListWidgetItem = cTabItem2 = QListWidgetItem(self.configTabWidget)
        cTabItem2.setText("Notification")
        cTabItem2.setTextAlignment(Qt.AlignHCenter)
        cTabItem2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.runtimeListWidgetItem = cTabItem3 = QListWidgetItem(self.configTabWidget)
        cTabItem3.setText("Runtime")
        cTabItem3.setTextAlignment(Qt.AlignHCenter)
        cTabItem3.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.voltageListWidgetItem = cTabItem4 = QListWidgetItem(self.configTabWidget)
        cTabItem4.setText("Voltage")
        cTabItem4.setTextAlignment(Qt.AlignHCenter)
        cTabItem4.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.selfTestListWidgetItem = cTabItem5 = QListWidgetItem(self.configTabWidget)
        cTabItem5.setText("Self-Test")
        cTabItem5.setTextAlignment(Qt.AlignHCenter)
        cTabItem5.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.advanceListWidgetItem = cTabItem6 = QListWidgetItem(self.configTabWidget)
        cTabItem6.setText("Advanced")
        cTabItem6.setTextAlignment(Qt.AlignHCenter)
        cTabItem6.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        cLayout = QVBoxLayout()
        cLayout.addWidget(self.configTabWidget)
        cLayout.addStretch(1)

        self.configTabWidget.selectionModel().currentChanged.connect(
            lambda: self.subPageSwitch(naviMenu.Configuration_Module.value))
        self.tapStackedWidget.addWidget(self.configTabWidget)

        # </editor-fold>

        # <editor-fold desc="Information子選單">

        self.infoTabWidget = QListWidget()
        self.infoTabWidget.setViewMode(QListView.IconMode)
        self.infoTabWidget.setFlow(0)
        self.infoTabWidget.setProperty('class', 'tabCls')
        self.infoTabWidget.setProperty('name', 'info')
        self.infoTabWidget.setFont(QFont("Roboto"))

        self.aboutListWidgetItem = cTabItem1 = QListWidgetItem(self.infoTabWidget)
        cTabItem1.setText("About")
        cTabItem1.setTextAlignment(Qt.AlignHCenter)
        cTabItem1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        cLayout = QVBoxLayout()
        cLayout.addWidget(self.infoTabWidget)
        cLayout.addStretch(1)

        self.infoTabWidget.selectionModel().currentChanged.connect(
            lambda: self.subPageSwitch(naviMenu.Information_Module.value))
        self.tapStackedWidget.addWidget(self.infoTabWidget)

        # </editor-fold>

        self.naviMenuIcons()  # 設定QListWidget中的子item

        # </editor-fold>

        # <editor-fold desc="Status Sidebar">

        statusVBox = QVBoxLayout()
        statusVBox.setObjectName("iconStatusBar")

        statusVBox_Sub_1 = QVBoxLayout()
        self.powerSrcImg = views.Custom.ViewData.ImageWidget(
            os.path.join(settings.IMAGE_PATH, "icon_power_source_3.png"),
            "Status_img", self)
        self.powerSrcImg.setAccessibleName("powersource")
        self.powerSourceLabel = statusLabel1_1 = QLabel(systemDefine.sideBarLabel_powerSourceStr)
        self.powerSourceLabel.setAccessibleName("powersourcelabel")
        statusLabel1_1.setProperty('class', 'Status_tilte')
        statusLabel1_1.setFont(QFont("Roboto"))
        self.powerSrcLbl = QLabel(systemDefine.unknownStr)
        self.powerSrcLbl.setProperty('class', 'Status_number')
        self.powerSrcLbl.setFont(QFont("Roboto"))
        statusVBox_Sub_1.addWidget(self.powerSrcImg)
        statusVBox_Sub_1.addWidget(statusLabel1_1)
        statusVBox_Sub_1.addWidget(self.powerSrcLbl)

        statusVBox_Sub_2 = QVBoxLayout()
        self.batteryImg = views.Custom.ViewData.ImageWidget(
            os.path.join(settings.IMAGE_PATH, "icon_battery_capacity_3.png"),
            "Status_img", self)
        self.batteryImg.setAccessibleName("batterycapacity")
        self.capacityLabel = statusLabel2_1 = QLabel(systemDefine.sideBarLabel_batteryCapacityStr)
        self.capacityLabel.setAccessibleName("batterycapacitylabel")
        self.capacityLabel.setFont(QFont("Roboto"))
        statusLabel2_1.setProperty('class', 'Status_tilte')
        self.batteryCapLbl = QLabel(systemDefine.noneValueStr + systemDefine.percentageStr)
        self.batteryCapLbl.setProperty('class', 'Status_number')
        self.batteryCapLbl.setFont(QFont("Roboto"))
        statusVBox_Sub_2.addWidget(self.batteryImg)
        statusVBox_Sub_2.addWidget(statusLabel2_1)
        statusVBox_Sub_2.addWidget(self.batteryCapLbl)

        statusVBox_Sub_3 = QVBoxLayout()
        self.runTimeImg = views.Custom.ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_runtime_3.png"),
                                                            "Status_img", self)
        self.runTimeImg.setAccessibleName("remainingruntime")
        self.runtimeLabel = statusLabel3_1 = QLabel(systemDefine.sideBarLabel_estimatedRuntimeStr)
        self.runtimeLabel.setAccessibleName("remainingruntimelabel")
        statusLabel3_1.setProperty('class', 'Status_tilte')
        statusLabel3_1.setFont(QFont("Roboto"))
        self.runtimeLbl = QLabel(systemDefine.noneValueStr + systemDefine.minStr)
        self.runtimeLbl.setProperty('class', 'Status_number')
        self.runtimeLbl.setFont(QFont("Roboto"))
        statusVBox_Sub_3.addWidget(self.runTimeImg)
        statusVBox_Sub_3.addWidget(statusLabel3_1)
        statusVBox_Sub_3.addWidget(self.runtimeLbl)

        statusVBox.addLayout(statusVBox_Sub_1)
        statusVBox.addLayout(statusVBox_Sub_2)
        statusVBox.addLayout(statusVBox_Sub_3)
        statusVBox.setContentsMargins(0, 20, 20, 0)
        statusVBox.setSpacing(0)

        # </editor-fold>

        titleWidget = CustomTitleWidget(self)
        titleWidget.setAccessibleName("ctitlew")
        titleWidget.position_change.connect(self.moveMe)
        titleWidget.setStyleSheet("background-color:#2B2B2B;max-height:40px;")
        titleWidget.close_minify_pressed.connect(self.close_minify)

        # <editor-fold desc="塞Master page所有物件">

        # ---Layout: Navi Menu母選單 + Status Bar---
        masterHLayout1 = QHBoxLayout()
        masterHLayout1.setObjectName("mainBar_hBoxLayout")
        masterHLayout1.addWidget(self.contentsWidget)
        masterHLayout1.addLayout(statusHBox)

        # ---Layout: 所有變動之頁面 + Status side bar---
        masterHLayout2 = QHBoxLayout()
        masterHLayout2.setObjectName("currentMainPage")
        masterHLayout2.addWidget(self.pagesWidget)
        masterHLayout2.addLayout(statusVBox)
        masterHLayout2.setContentsMargins(0, 0, 0, 0)
        masterHLayout2.setSpacing(0)
        # masterHLayout2.addStretch(1)

        # ---Layout: 頁面所有layout堆疊在一起---
        masterVLayout = QVBoxLayout()
        masterVLayout.setObjectName("mainBar_vBoxLayout")
        masterVLayout.addWidget(titleWidget)
        titleWidget.show()
        masterVLayout.addLayout(masterHLayout1)
        masterVLayout.addWidget(self.tapStackedWidget, 1)
        masterVLayout.addLayout(masterHLayout2, 1)
        masterVLayout.setContentsMargins(0, 0, 0, 0)
        masterVLayout.setSpacing(0)

        testHLayout2 = QHBoxLayout()
        footerImage = views.Custom.ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "footer.png"), "footer",
                                                        self)
        footerImage.setAccessibleName("footer")
        testHLayout2.addWidget(footerImage)  # footer
        masterVLayout.addLayout(testHLayout2, 1)

        masterVLayout.setContentsMargins(0, 0, 0, 0)
        masterVLayout.setSpacing(0)

        # </editor-fold>

        # <editor-fold desc="預設畫面狀態">

        daemonStatus = DaemonStatus.DaemonStatus()
        daemonStatus.deviceId = -1
        daemonStatus.isDaemonStarted = False

        self.updateCurrentStatusPage(None)
        self.energyReportingPage.updatePageByStatus(daemonStatus)
        self.schedulePage.updatePageByStatus(daemonStatus)
        self.notificationPage.updatePageByStatus(daemonStatus)
        self.runtimePage.updatePageByStatus(daemonStatus)
        self.selfTestPage.updatePageByStatus(daemonStatus)
        self.advancedPage.updatePageByStatus(daemonStatus)
        self.summaryPage.updatePageByStatus(daemonStatus)
        self.voltagePage.updatePageByStatus(daemonStatus)

        # </editor-fold>

        self.setLayout(masterVLayout)
        self.setWindowTitle("POWERPANEL Personal")

    """設定Navi Menu母選單圖片與event"""

    def closeEvent(self, QCloseEvent):
        self.setHidden(True)
        QCloseEvent.ignore()

    def naviMenuIcons(self):

        self.monitorBtn = QListWidgetItem(self.contentsWidget)
        self.monitorBtn.setIcon(QIcon(os.path.join(settings.IMAGE_PATH, "btn_monitor.png")))
        self.monitorBtn.setTextAlignment(Qt.AlignHCenter)
        self.monitorBtn.setFlags(Qt.ItemIsEnabled)  # 2017/07/19 Kenneth Edit

        self.energyBtn = QListWidgetItem(self.contentsWidget)
        self.energyBtn.setIcon(QIcon(os.path.join(settings.IMAGE_PATH, "btn_energy.png")))
        self.energyBtn.setTextAlignment(Qt.AlignHCenter)
        self.energyBtn.setFlags(Qt.ItemIsEnabled)  # 2017/07/19 Kenneth Edit

        self.configBtn = QListWidgetItem(self.contentsWidget)
        self.configBtn.setIcon(QIcon(os.path.join(settings.IMAGE_PATH, "btn_configure.png")))
        self.configBtn.setTextAlignment(Qt.AlignHCenter)
        self.configBtn.setFlags(Qt.ItemIsEnabled)  # 2017/07/19 Kenneth Edit

        self.helpBtn = QListWidgetItem(self.contentsWidget)
        self.helpBtn.setIcon(QIcon(os.path.join(settings.IMAGE_PATH, "btn_help.png")))
        self.helpBtn.setTextAlignment(Qt.AlignHCenter)
        self.helpBtn.setFlags(Qt.ItemIsEnabled)  # 2017/07/19 Kenneth Edit

        self.openListWidget("monitor")  # 設定一開始QListWidget出現index
        self.contentsWidget.itemClicked.connect(self.mainPageSwitch)

    def overviewStatusUpdate(self, daemonDown):

        self.daemonDown = daemonDown

        if daemonDown:
            if not daemonDown.isDaemonStarted:
                statusPix_top = QPixmap(self.statusNotReadyImage_top)
                # statusTxt_top = systemDefine.pppe_notReadyStr
                statusTxt_top = self.getTranslateString(i18nId.i18nId().PowerPanel_Personal_Edition_Service_is_not_ready)

            elif daemonDown.deviceId == -1:
                statusPix_top = QPixmap(self.statusUnableImage_top)
                # statusTxt_top = systemDefine.ups_unable_communicationStr
                statusTxt_top = self.getTranslateString(i18nId.i18nId().Unable_to_establish_communication_with_UPS)

            elif daemonDown.deviceId != -1:
                statusPix_top = QPixmap(self.statusNormalImage_top)
                # statusTxt_top = systemDefine.ups_working_normallyStr
                statusTxt_top = self.getTranslateString(i18nId.i18nId().The_UPS_is_working_normally)
        else:
            statusPix_top = QPixmap(self.statusNotReadyImage_top)
            # statusTxt_top = systemDefine.pppe_notReadyStr
            statusTxt_top = self.getTranslateString(i18nId.i18nId().PowerPanel_Personal_Edition_Service_is_not_ready)
            Logger.LogIns().logger.info("toogle status to service is not ready - not daemonDown")

        Logger.LogIns().logger.info("set status label: "+str(statusTxt_top))
        # top bar
        self.statusImage_top.label.setPixmap(statusPix_top)
        self.statusLabel_top.setText(statusTxt_top)

    def updateNoDaemonSideBar(self):
        powerFrom_side = self.getTranslateString(i18nId.i18nId().Unknown)
        battery_capacity = systemDefine.noneValueStr
        remain_runtime = systemDefine.noneValueStr
        powerSrcPix_side = QPixmap(self.powerSrcNoOut)
        batteryCapPix_side = QPixmap(self.batteryCapLowImg)
        runtimePix_side = QPixmap(self.runTimeDisableImg)

        self.powerSrcImg.label.setPixmap(powerSrcPix_side)
        self.batteryImg.label.setPixmap(batteryCapPix_side)
        self.runTimeImg.label.setPixmap(runtimePix_side)
        self.powerSrcLbl.setText(powerFrom_side)
        self.batteryCapLbl.setText(str(battery_capacity) + systemDefine.percentageStr)
        if not systemFunction.stringIsNullorEmpty(remain_runtime):
            self.runtimeLbl.setText(str(remain_runtime) +  " " + self.getTranslateString(i18nId.i18nId().min))

    """更新Status Sidebar資訊"""

    def updateStatusSideBar(self, deviceStatus):
        self.deviceStatus = deviceStatus

        powerFrom_side = self.getTranslateString(i18nId.i18nId().Unknown)
        battery_capacity = systemDefine.noneValueStr
        remain_runtime = systemDefine.noneValueStr
        powerSrcPix_side = QPixmap(self.powerSrcNoOut)
        batteryCapPix_side = QPixmap(self.batteryCapLowImg)
        runtimePix_side = QPixmap(self.runTimeDisableImg)

        # <editor-fold desc="處理畫面資料呈現">
        if deviceStatus.deviceId == -1:

            powerFrom_side = self.getTranslateString(i18nId.i18nId().Unknown)
            battery_capacity = systemDefine.noneValueStr
            remain_runtime = systemDefine.noneValueStr
            powerSrcPix_side = QPixmap(self.powerSrcNoOut)
            batteryCapPix_side = QPixmap(self.batteryCapLowImg)
            runtimePix_side = QPixmap(self.runTimeDisableImg)

        else:

            if deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.UtilityPower.value:

                powerFrom_side = self.getTranslateString(i18nId.i18nId().AC_Utility)
                powerSrcPix_side = QPixmap(self.powerSrcNormal)
                batteryCapPix_side = QPixmap(self.batteryCapFullImg)
                runtimePix_side = QPixmap(self.runTimeNormalImg)

            elif deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.BatteryPower.value:

                powerFrom_side = self.getTranslateString(i18nId.i18nId().Battery)
                powerSrcPix_side = QPixmap(self.powerSrcBattery)
                batteryCapPix_side = QPixmap(self.batteryCapNoFullImg)
                runtimePix_side = QPixmap(self.runTimeAbnormalImg)

            elif deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.NoOutput.value:

                powerFrom_side = self.getTranslateString(i18nId.i18nId().Battery)
                powerSrcPix_side = QPixmap(self.powerSrcNoOut)
                batteryCapPix_side = QPixmap(self.batteryCapLowImg)
                runtimePix_side = QPixmap(self.runTimeDisableImg)

            if not systemFunction.stringIsNullorEmpty(deviceStatus.BatteryCapacity):
                battery_capacity = "{0:.0f}%".format(systemFunction.stringParse2Float(deviceStatus.BatteryCapacity))

            if not systemFunction.stringIsNullorEmpty(deviceStatus.RemainingRuntime):
                remain_runtime = round(systemFunction.stringParse2Min(deviceStatus.RemainingRuntime))
            # else:
            #     remain_runtime = None

        # </editor-fold>

        # <editor-fold desc="Data binding">

        # side bar
        self.powerSrcImg.label.setPixmap(powerSrcPix_side)
        self.batteryImg.label.setPixmap(batteryCapPix_side)
        self.runTimeImg.label.setPixmap(runtimePix_side)
        self.powerSrcLbl.setText(powerFrom_side)
        self.batteryCapLbl.setText(str(battery_capacity))
        if not systemFunction.stringIsNullorEmpty(remain_runtime):
            self.runtimeLbl.setText(str(remain_runtime) + " " + self.getTranslateString(i18nId.i18nId().min))

        # </editor-fold>

    """進行主頁面切換"""

    def mainPageSwitch(self, item):
        index = self.contentsWidget.row(item)
        if index == 0:
            self.pagesWidget.setCurrentIndex(0)
            self.openListWidget(systemDefine.PAGE_MONITOR)
            # 2019/02/23 Kenneth Setting class for Qss
            self.contentsWidget.setProperty('class', 'mainTabCls1')

        elif index == 1:
            self.pagesWidget.setCurrentIndex(3)
            self.openListWidget(systemDefine.PAGE_ENERGY)
            # 2019/02/23 Kenneth Setting class for Qss
            self.contentsWidget.setProperty('class', 'mainTabCls2')

        elif index == 2:
            self.pagesWidget.setCurrentIndex(5)
            self.openListWidget(systemDefine.PAGE_CONFIG)
            # 2019/02/23 Kenneth Setting class for Qss
            self.contentsWidget.setProperty('class', 'mainTabCls3')

        elif index == 3:
            self.openListWidget("info")
            self.openListWidget(systemDefine.PAGE_INFO)
            self.pagesWidget.setCurrentIndex(12)
            # 2019/02/23 Kenneth Setting class for Qss
            self.contentsWidget.setProperty('class', 'mainTabCls4')

        # 2019/02/23 Kenneth
        self.contentsWidget.style().polish(self.contentsWidget)
        self.tapStackedWidget.setCurrentIndex(self.contentsWidget.row(item))

    """進行子頁面切換"""

    def openListWidget(self, listWidgetName):
        for listWidget in self.tapStackedWidget.children():
            if listWidget.property('name') == systemDefine.PAGE_CONFIG == listWidgetName:
                listWidget.setCurrentRow(-1)
            else:
                if listWidget.property('name') == listWidgetName:
                    listWidget.setCurrentRow(0)

    def subPageSwitch(self, mainPage):

        naviMenu = views.Custom.ViewData.NaviMenu

        if mainPage == naviMenu.Monitor_Module.value:
            index = self.monitorTabWidget.currentRow()
            # print(index)
            self.pagesWidget.setCurrentIndex(index)
        elif mainPage == naviMenu.Energy_Module.value:
            index = self.energyTabWidget.currentRow() + 3
            # print(index)
            self.pagesWidget.setCurrentIndex(index)
        elif mainPage == naviMenu.Configuration_Module.value:
            index = self.configTabWidget.currentRow() + 6
            # print(index)
            self.pagesWidget.setCurrentIndex(index)
        elif mainPage == naviMenu.Information_Module.value:
            index = self.infoTabWidget.currentRow() + 12
            # print(index)
            self.pagesWidget.setCurrentIndex(index)

    # --------------------------以下為更新畫面method--------------------------

    """更新CurrentStatus資訊"""

    def updateCurrentStatusPage(self, deviceStatus):
        self.currentStatusPage.updatePage(deviceStatus)
        self.voltagePage.updateCurrentVoltage(deviceStatus)

    """更新About"""

    def updateAboutPage(self, updateData):
        self.aboutPage.updatePage(updateData)

    def disableConfigure(self):
        self.notificationPage.disableConfigure()

    def renderText(self):
        self.powerSourceLabel.setText(self.getTranslateString(i18nId.i18nId().Power_Source))
        self.capacityLabel.setText(self.getTranslateString(i18nId.i18nId().Battery_Capacity))
        self.runtimeLabel.setText(self.getTranslateString(i18nId.i18nId().Estimated_Runtime))
        self.statusListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Current_Status))
        self.summaryListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Summary))
        self.scheduleListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Schedule))
        self.notifyListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Notification))
        self.runtimeListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Runtime))
        self.voltageListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Voltage))
        self.selfTestListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Self_Test))
        self.advanceListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Advanced))
        self.aboutListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().About))
        self.energyReportListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Energy_Reporting))
        self.energySettingListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Energy_Settings))
        self.eventLogsListWidgetItem.setText(self.getTranslateString(i18nId.i18nId().Event_Logs))

        self.configTabWidget.repaint()
        self.configTabWidget.setStyleSheet("background-position: left center;")
        self.monitorTabWidget.repaint()
        self.monitorTabWidget.setStyleSheet("background-position: left center;")
        self.energyTabWidget.repaint()
        self.energyTabWidget.setStyleSheet("background-position: left center;")
        self.infoTabWidget.repaint()
        self.infoTabWidget.setStyleSheet("background-position: left center;")

        # if self.daemonDown is not None:
        #     self.overviewStatusUpdate(self.daemonDown)

        self.overviewStatusUpdate(self.daemonDown)

        if self.deviceStatus is not None:
            self.updateStatusSideBar(self.deviceStatus)

    def getTranslateString(self, id):
        return self.i18nTranslater.getTranslateString(id)

    # 不同平台支援的字體不同, 透過QFontDatabase來確認是否支援
    def isFontAvailable(self, font_name):
        instance = QFontDatabase()
        fontList = QFontDatabase.families(instance)
        if font_name in fontList:
            return True
        return False

    def reRender(self, localeStr):
        try:
            font_name = settings.FONT_DEFAULT
            # 依據locale變更對應的字型
            if localeStr == appLocaleData.appLocaleData().ja_JP:
                if self.isFontAvailable(settings.FONT_MS_JP):
                    font_name = settings.FONT_MS_JP

            font = QFont(font_name)
            font.setPixelSize(settings.FONT_SIZE_IN_PX);
            font.setWeight(QFont.Normal);
            QApplication.setFont(QFont(font_name), "QWidget")

            if self.lastTranslator:
                removeFlag = QApplication.removeTranslator(self.lastTranslator)
                # print(str(removeFlag))

            # set context menu i18n
            translator = QTranslator()
            file = "qtbase_" + appLocaleData.appLocaleRecorder().appLocale
            # print(str(file))

            loadFlag = translator.load(file, settings.CONTEXT_MENU_PATH)
            # print(str(loadFlag))

            installFlag = QApplication.installTranslator(translator)
            # print(str(installFlag))

            self.lastTranslator = translator

            # re render all page
            for widget in self.pagesWidget.children():
                if "reRender" in dir(widget):
                    widget.reRender(localeStr)

            self.i18nTranslater = i18nTranslater.i18nTranslater(localeStr)
            self.renderText()
            self.aboutPage.ChangeUrlLinkBylocale(localeStr)
            self.configrationMainPage.ChangePhotoLinkBylocale(localeStr)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    @pyqtSlot(int, int)
    def moveMe(self, x, y):
        self.move(x, y)

    @pyqtSlot(str)
    def close_minify(self, purpose):
        print("base widget close minify")
        print(purpose)
        if purpose == "hide":
            self.hide()
        elif purpose == "close":
            self.quit_triggered.emit()
        elif purpose == "minimize":
            if platform.system() == 'Darwin':
                # QTBUG-64994, it can not handle showMinimized() well, and caused window display failure
                pass
            else:
                print("inside minimize")
                self.showMinimized()
        else:
            pass
