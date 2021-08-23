import sys
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QRadioButton, QPushButton)

from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.Custom import ViewData
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox

class Runtime(TemplatePage.TemplatePage):
    _setRuntimeSignal = pyqtSignal(object, object)

    def __init__(self):
        super(Runtime, self).__init__()
        self.setAccessibleName("runtimepage")
        self.configGroup = None
        self.RuntimeMesgLabel = None
        self.keepRunBtn = None
        self.keepRunMsgLabel = None
        self.keepRunMsg2Label = None
        self.preserveBtn = None
        self.preserveLabel = None
        self.preserveUnitLabel = None
        self.preserve2Label = None

        self.init_ui()

    def init_ui(self):

        # <editor-fold desc="Current Status UI: Main data fields">

        self.configGroup = configGroup = QGroupBox()
        configGroup.setObjectName("runtimeQGroupBox")
        self.configGroup.setAccessibleName("runtimepagegroup")
        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("runtimepagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("runtime.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        self.RuntimeMesgLabel = serverLabel_1 = QLabel()
        serverLabel_1.setFont(QFont("Roboto", 8, QFont.Bold))
        serverLabel_1.setProperty('class', 'label-LeftCls')
        serverLabel_1.setWordWrap(True)

        serverLayout1 = QHBoxLayout()
        serverLayout1.addWidget(serverLabel_1)

        # <editor-fold desc="Radio Btn">

        vLayout1 = QVBoxLayout()
        hLayout1 = QHBoxLayout()

        self.keepRunBtn = QRadioButton()
        self.keepRunBtn.setAccessibleName("runtimepagekeepcomputerrun")
        # self.keepRunBtn.setFixedWidth(205)
        self.keepRunBtn.clicked.connect(lambda: self.whichbtn(self.keepRunBtn))
        self.keepRunMsgLabel = label1_1 = QLabel()
        self.keepRunDDL = keepRunDDL = ComboBox()
        self.keepRunDDL.setAccessibleName("runtimepagekeepcomputerrunselect")
        for val in ViewData.keepRunDDL:
            keepRunDDL.addItem(str(val), val)

        keepRunDDL.setProperty('class', 'runtimepagekeepcomputerrunselect')
        self.keepRunDDL.activated.connect(lambda: self.whichbtn(self.keepRunDDL))

        self.minLabel = QLabel()
        self.keepRunMsg2Label = label1_3 = QLabel()
        self.keepRunMsg2Label.setWordWrap(True)

        hLayout1.addWidget(label1_1)
        hLayout1.addWidget(keepRunDDL)
        hLayout1.addWidget(self.minLabel)
        hLayout1.addStretch(1)
        vLayout1.addWidget(self.keepRunBtn)
        vLayout1.addLayout(hLayout1)
        vLayout1.addWidget(label1_3)
        vLayout1.addStretch(1)

        """------------------------------------------Separator-------------------------------------------------------"""

        vLayout2 = QVBoxLayout()
        hLayout2 = QHBoxLayout()

        self.preserveBtn = QRadioButton()
        self.preserveBtn.setAccessibleName("runtimepagepreservebatterypower")
        self.preserveBtn.clicked.connect(lambda: self.whichbtn(self.preserveBtn))
        self.preserveBtn.setProperty('class', 'preserveBtn')
        # width2 = self.preserveBtn.width()
        # self.preserveBtn.setFixedWidth(200)
        self.preserveLabel = label2_1 = QLabel()
        self.preserveDDL = preserveDDL = ComboBox()
        self.preserveDDL.setAccessibleName("runtimepagepreservebatterypowerselect")
        for i in range(0, 6, 1):
            preserveDDL.addItem(str(i), i)

        preserveDDL.addItem(str(10), 10)  # 新增10分鐘的選項
        preserveDDL.addItem(str(15), 15)  # 新增15分鐘的選項
        preserveDDL.addItem(str(20), 20)  # 新增20分鐘的選項
        preserveDDL.setProperty('class', 'runtimepagepreservebatterypowerselect')
        self.preserveDDL.activated.connect(lambda: self.whichbtn(self.preserveDDL))

        self.preserveUnitLabel = QLabel()
        self.preserve2Label = label2_3 = QLabel()
        # 2019/02/23 Kenneth
        self.preserve2Label.setWordWrap(True)
        self.preserve2Label.setProperty('class', 'preserve2Label')

        hLayout2.addWidget(label2_1)
        hLayout2.addWidget(preserveDDL)
        hLayout2.addWidget(self.preserveUnitLabel)
        hLayout2.addStretch(1)
        vLayout2.addWidget(self.preserveBtn)
        vLayout2.addLayout(hLayout2)
        vLayout2.addWidget(label2_3)
        vLayout2.addStretch(1)

        # self.setLayout(layout)

        # </editor-fold>

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(serverLayout1)
        serverLayoutAll.addLayout(vLayout1)
        serverLayoutAll.addLayout(vLayout2)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        # serverLayoutAll.setSpacing(0)
        configGroup.setLayout(serverLayoutAll)

        # </editor-fold>

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setObjectName("currentStatusMain")
        mainLayout.addWidget(configGroup)
        mainLayout.addStretch(1)

        self.renderText()

        self.setLayout(mainLayout)

    @property
    def setRuntimeSignal(self):
        return self._setRuntimeSignal

    @setRuntimeSignal.setter
    def setRuntimeSignal(self, value):
        self._setRuntimeSignal = value

    def whichbtn(self, b):
        try:
            if self.keepRunBtn.isChecked():
                runtimeType = ViewData.RuntimeSettingEnum.KeepComputerRunning.value
                runtimeCountdownTime = int(self.keepRunDDL.currentData())

            elif self.preserveBtn.isChecked():
                runtimeType = ViewData.RuntimeSettingEnum.PreserveBatteryPower.value
                runtimeCountdownTime = int(self.preserveDDL.currentData())

            self._setRuntimeSignal.emit(runtimeType, runtimeCountdownTime)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def restoreConfigSetting(self, config):
        if config.runtimeType == ViewData.RuntimeSettingEnum.KeepComputerRunning.value:
            self.keepRunBtn.setChecked(True)
            # index = self.keepRunDDL.findText(str(config.runtimeCountdownTime), QtCore.Qt.MatchFixedString)
            # if index >= 0:
            #     self.keepRunDDL.setCurrentIndex(index)
        else:
            self.preserveBtn.setChecked(True)
            index = self.preserveDDL.findText(str(config.runtimeCountdownTime), QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.preserveDDL.setCurrentIndex(index)

    def updatePageByStatus(self, daemonStatus):

        disabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            pass

        elif daemonStatus and daemonStatus.deviceId == -1:
            pass

        elif daemonStatus and daemonStatus.deviceId != -1:
            disabledFlag = False

        self.keepRunBtn.setDisabled(disabledFlag)
        self.keepRunDDL.setDisabled(disabledFlag)
        self.preserveBtn.setDisabled(disabledFlag)
        self.preserveDDL.setDisabled(disabledFlag)

    def updatePage(self, updateData):
        isContainItem = False
        if updateData.batteryRuntime is not None or updateData.batteryRuntime != -1:
            currentBatteryRuntimeInt = int((updateData.batteryRuntime / 60))
            currentBatteryRuntimeStr = str(currentBatteryRuntimeInt)
            self.keepRunDDL.clear()

            # check runtime range, if empty, default list is 5,6,7,8
            if len(updateData.batteryRuntimeRange) == 0:
                updateData.batteryRuntimeRange = [300,360,420,480]
            for val in updateData.batteryRuntimeRange:
                val = int(val / 60)
                if val != 0:
                   if val == currentBatteryRuntimeInt:
                           isContainItem = True
                   self.keepRunDDL.addItem(str(val), val)
            if not isContainItem:
                self.keepRunDDL.addItem(currentBatteryRuntimeStr, currentBatteryRuntimeInt)
                self.keepRunDDL.setCurrentText(currentBatteryRuntimeStr)
        if isContainItem:
            self.keepRunDDL.setCurrentText(currentBatteryRuntimeStr)
        print(updateData.batteryRuntimeRange)

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Runtime_Configuration))
        self.RuntimeMesgLabel.setText(self.getTranslateString(
            i18nId.i18nId().You_can_change_the_length_of_time_that_application_short_name_allows_your_UPS_to_run_on_battery_power))
        self.keepRunBtn.setText(self.getTranslateString(i18nId.i18nId().Keep_Computer_Running))

        wordingArr1 = self.getTranslateString(
            i18nId.i18nId().Shutdown_this_computer_when_remaining_battery_runtime_is_only_xxxx_minutes).split("xxxx")
        self.keepRunMsgLabel.setText(wordingArr1[0])
        self.minLabel.setText(wordingArr1[1])

        self.keepRunMsg2Label.setText(
            self.getTranslateString(i18nId.i18nId().Use_this_Option_to_extend_operating_time_while_on_battery_power))
        self.preserveBtn.setText(self.getTranslateString(i18nId.i18nId().Preserve_Battery_Power))

        wordingArr2 = self.getTranslateString(
            i18nId.i18nId().Shutdown_this_computer_after_UPS_runs_on_battery_power_for_xxxx_minutes).split("xxxx")
        self.preserveLabel.setText(wordingArr2[0])
        self.preserveUnitLabel.setText(wordingArr2[1])

        self.preserve2Label.setText(
            self.getTranslateString(i18nId.i18nId().Use_this_option_to_save_battery_power_for_successive_power_outages))
