import datetime
import traceback
import sys
from functools import partial
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QWidget, QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView,
                             QCheckBox, QPushButton)

from System import settings, systemFunction
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.Custom import ViewData
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox

class Schedule(TemplatePage.TemplatePage):
    _setScheduleSignal = pyqtSignal(object)

    def __init__(self):
        super(Schedule, self).__init__()
        self.configGroup = None
        self.scheduleMsgLabel = None
        self.scheduleTable = None
        self.shutdownData = None
        self.restartData = None
        self.setAccessibleName("schedulepage")
        self.init_ui()

    def init_ui(self):

        # <editor-fold desc="Summary UI: label & DDL">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("scheduleQGroupBox")
        self.configGroup.setAccessibleName("schedulepagegroup")

        mainTitleLayout = QHBoxLayout()
        # self.mainTitle = mainTitle = QLabel("Schedule")
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("schedulepagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("schedule.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        # self.scheduleMsgLabel = serverLabel_1 = QLabel(
        #     " You can decide when you computer, UPS and connected equipment will turn ON and Off")
        self.scheduleMsgLabel = serverLabel_1 = QLabel()
        serverLabel_1.setProperty('class', 'label-LeftCls')
        serverLabel_1.setWordWrap(True)


        self.scheduleDescription = QLabel("")
        self.scheduleDescription.setProperty('class', 'label-scheduleDescription')
        self.scheduleDescription.setWordWrap(True)

        serverLayout1 = QVBoxLayout()
        serverLayout1.addWidget(serverLabel_1)
        serverLayout1.addWidget(self.scheduleDescription)
        serverLayout1.addStretch(1)

        # </editor-fold>

        # <editor-fold desc="Table">

        self.scheduleTable = QTableWidget(7, 6)
        # self.scheduleTable.setHorizontalHeaderLabels(['Days', 'ON', "(Act.)", 'OFF', "(N.R)", "(Act.)"])
        self.scheduleTable.setObjectName("scheduleTable")
        self.scheduleTable.verticalHeader().setVisible(False)
        self.scheduleTable.setFocusPolicy(0)
        self.scheduleTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scheduleTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.scheduleTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.scheduleTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.scheduleTable.setAlternatingRowColors(True)
        # self.scheduleTable.setStyleSheet("alternate-background-color: yellow; background-color: red;")

        self.scheduleTable.setColumnWidth(0, 105)
        self.scheduleTable.setColumnWidth(1, 152)
        self.scheduleTable.setColumnWidth(2, 50)
        self.scheduleTable.setColumnWidth(3, 150)
        self.scheduleTable.setColumnWidth(4, 55)
        # Kenneth 2020/06/30 邊框調整
        self.scheduleTable.setColumnWidth(5, 58)
        self.scheduleTable.setMinimumHeight(275)
        self.scheduleTable.setRowHeight(0, 35)
        self.scheduleTable.setRowHeight(1, 35)
        self.scheduleTable.setRowHeight(2, 35)
        self.scheduleTable.setRowHeight(3, 35)
        self.scheduleTable.setRowHeight(4, 35)
        self.scheduleTable.setRowHeight(5, 35)
        self.scheduleTable.setRowHeight(6, 35)

        # Kenneth 20170725 修改表格中checkbox背景
        self.scheduleTable.setSortingEnabled(False)

        self.onDDL = []
        self.offDDL = []
        self.onActionCheck = []
        self.offActionCheck = []
        self.offNRCheck = []

        for index, item in enumerate(settings.week):
            if index == 6:  # sunday
                newIndex = 0
            else:
                newIndex = index + 1

            colon = QTableWidgetItem(":")
            # self.scheduleTable.setItem(newIndex, 0, QTableWidgetItem(str(item)))

            self.onDDL.append(index)
            self.onDDL[index] = PeriodDDL(True)
            self.onDDL[index].onHourDDL.activated.connect(partial(self.whichBtn))
            self.onDDL[index].onMinDDL.activated.connect(partial(self.whichBtn))
            self.scheduleTable.setCellWidget(newIndex, 1, self.onDDL[index])

            self.onActionCheck.append(index)
            self.onActionCheck[index] = QCheckBox("")
            self.onActionCheck[index].clicked.connect(
                partial(self.whichBtn))
            self.scheduleTable.setCellWidget(newIndex, 2, self.onActionCheck[index])

            self.offDDL.append(index)
            self.offDDL[index] = PeriodDDL(False)
            self.offDDL[index].offHourDDL.activated.connect(partial(self.whichBtn))
            self.offDDL[index].offMinDDL.activated.connect(partial(self.whichBtn))
            self.scheduleTable.setCellWidget(newIndex, 3, self.offDDL[index])

            self.offNRCheck.append(index)
            self.offNRCheck[index] = QCheckBox("")
            self.offNRCheck[index].clicked.connect(partial(self.whichBtn))
            self.scheduleTable.setCellWidget(newIndex, 4, self.offNRCheck[index])

            self.offActionCheck.append(index)
            self.offActionCheck[index] = QCheckBox("")
            self.offActionCheck[index].clicked.connect(partial(self.whichBtn))
            self.scheduleTable.setCellWidget(newIndex, 5, self.offActionCheck[index])

            layout = QHBoxLayout()
            layout.addWidget(self.scheduleTable)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(serverLayout1)
        serverLayoutAll.addLayout(layout)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        serverLayoutAll.setSpacing(0)

        # </editor-fold>

        configGroup.setLayout(serverLayoutAll)
        # serverLayoutAll.addStretch(1)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setObjectName("currentStatusMain")
        mainLayout.addWidget(configGroup)
        mainLayout.addStretch(0)
        self.renderText()
        self.setLayout(mainLayout)

    @property
    def setScheduleSignal(self):
        return self._setScheduleSignal

    @setScheduleSignal.setter
    def setScheduleSignal(self, value):
        self._setScheduleSignal = value

    def whichBtn(self):
        try:
            data = self.getScheduleData()
            self._setScheduleSignal.emit(data)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def getScheduleData(self):
        dic = dict()

        for index, item in enumerate(settings.week):
            data = ViewData.ScheduleData()
            data.days = item
            data.onTimeHour = int(self.onDDL[index].onHourDDL.currentData())
            data.onTimeMin = int(self.onDDL[index].onMinDDL.currentData())
            data.offTimeHour = int(self.offDDL[index].offHourDDL.currentData())
            data.offTimeMin = int(self.offDDL[index].offMinDDL.currentData())
            data.onAction = self.onActionCheck[index].isChecked()
            data.offAction = self.offActionCheck[index].isChecked()
            data.noneReset = self.offNRCheck[index].isChecked()
            dic[item] = data

        return dic

    def updateTable(self, displayDic):
        periodDDL = PeriodDDL(True)
        ddlHourContent = periodDDL.ddlHourContent()
        ddlMinContent = periodDDL.ddlMinContent()

        for index, item in enumerate(settings.week):

            displayData = displayDic[item]

            onHourDDLText = list(ddlHourContent.keys())[list(ddlHourContent.values()).index(displayData.onTimeHour)]
            onHourIndex = self.onDDL[index].onHourDDL.findText(onHourDDLText, QtCore.Qt.MatchFixedString)
            if onHourIndex >= 0:
                self.onDDL[index].onHourDDL.setCurrentIndex(onHourIndex)

            onMinDDLText = list(ddlMinContent.keys())[list(ddlMinContent.values()).index(displayData.onTimeMin)]
            onMinIndex = self.onDDL[index].onMinDDL.findText(onMinDDLText, QtCore.Qt.MatchFixedString)
            if onMinIndex >= 0:
                self.onDDL[index].onMinDDL.setCurrentIndex(onMinIndex)

            offHourDDLText = list(ddlHourContent.keys())[list(ddlHourContent.values()).index(displayData.offTimeHour)]
            offHourIndex = self.offDDL[index].offHourDDL.findText(offHourDDLText, QtCore.Qt.MatchFixedString)
            if offHourIndex >= 0:
                self.offDDL[index].offHourDDL.setCurrentIndex(offHourIndex)

            offMinDDLText = list(ddlMinContent.keys())[list(ddlMinContent.values()).index(displayData.offTimeMin)]
            offMinIndex = self.offDDL[index].offMinDDL.findText(offMinDDLText, QtCore.Qt.MatchFixedString)
            if offMinIndex >= 0:
                self.offDDL[index].offMinDDL.setCurrentIndex(offMinIndex)

            if displayData.onAction:
                self.onActionCheck[index].setChecked(True)
            else:
                self.onActionCheck[index].setChecked(False)

            if displayData.offAction:
                self.offActionCheck[index].setChecked(True)
            else:
                self.offActionCheck[index].setChecked(False)

            if displayData.noneReset:
                self.offNRCheck[index].setChecked(True)
            else:
                self.offNRCheck[index].setChecked(False)

    def updateDescription(self, shutdown, restart):
        text = ""
        # if shutdown is not None:
        #     weekStrData1 = self.isDatetimeWithinThisWeek(shutdown.offTime)
        #     text += "Your computer will be shut down at " + str(shutdown.offTime.strftime("%I:%M %p"))
        #     text += " on " + weekStrData1[1] + settings.week[shutdown.offTime.weekday()] + weekStrData1[0]
        #
        # if restart is not None:
        #     weekStrData2 = self.isDatetimeWithinThisWeek(restart.onTime)
        #     text += " and restart at " + str(restart.onTime.strftime("%I:%M %p"))
        #     text += "\non " + weekStrData2[1] + settings.week[restart.onTime.weekday()] + weekStrData2[0]

        if shutdown is not None:
            # text += "Your computer will be shut down at " + str(shutdown.offTime.strftime("%Y/%m/%d %I:%M %p")) + " on "
            # text += settings.week[shutdown.offTime.weekday()]
            self.shutdownData = shutdown
            text = self.getTranslateString(i18nId.i18nId().Your_computer_will_be_shut_down_at_xxxx0_on_xxxx1_xxxx2).replace(
                "xxxx0", str(shutdown.offTime.strftime("%Y/%m/%d %I:%M %p"))).replace(
                "xxxx1 xxxx2", self.GetWeekDayI18n(shutdown.offTime.weekday()))
        else:
            self.shutdownData = None

        if restart is not None:
            self.restartData = restart
            # text += " and restart at \n" + str(restart.onTime.strftime("%Y/%m/%d %I:%M %p")) + " on "
            # text += settings.week[restart.onTime.weekday()]

            text = "<p>" + self.getTranslateString(
                i18nId.i18nId().Your_computer_will_be_shut_down_at_xxxx0_on_xxxx1_xxxx2_and_restart_at_xxxx3_on_xxxx4_xxxx5).replace(
                "xxxx0", str(shutdown.offTime.strftime("%Y/%m/%d %I:%M %p"))).replace(
                "xxxx1 xxxx2", self.GetWeekDayI18n(shutdown.offTime.weekday())).replace(
                "xxxx3", str("<br>" + restart.onTime.strftime("%Y/%m/%d %I:%M %p"))).replace(
                "xxxx4 xxxx5", self.GetWeekDayI18n(restart.onTime.weekday())) + "</p>"
            self.scheduleDescription.setProperty("class", "label-scheduleDescription")
        else:
            self.restartData = None
            self.scheduleDescription.setProperty("class", "label-scheduleDescription2")
            text += "\n "  # 因為CSS排版需要而加

        self.scheduleDescription.style().polish(self.scheduleDescription)
        self.scheduleDescription.setText(text)

    def GetWeekDayI18n(self, index):
        return {
            0: self.getTranslateString(i18nId.i18nId().Monday),
            1: self.getTranslateString(i18nId.i18nId().Tuesday),
            2: self.getTranslateString(i18nId.i18nId().Wednesday),
            3: self.getTranslateString(i18nId.i18nId().Thursday),
            4: self.getTranslateString(i18nId.i18nId().Friday),
            5: self.getTranslateString(i18nId.i18nId().Saturday),
            6: self.getTranslateString(i18nId.i18nId().Sunday)
        }.get(index, "")


    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Schedule))
        self.scheduleMsgLabel.setText(self.getTranslateString(
            i18nId.i18nId().You_can_decide_what_time_your_computer_and_equipment_will_turn_ON_and_OFF))
        self.scheduleTable.setHorizontalHeaderLabels([self.getTranslateString(i18nId.i18nId().Days),
                                                      self.getTranslateString(i18nId.i18nId().ON),
                                                      self.getTranslateString(i18nId.i18nId().Act),
                                                      self.getTranslateString(i18nId.i18nId().OFF),
                                                      self.getTranslateString(i18nId.i18nId().NR),
                                                      self.getTranslateString(i18nId.i18nId().Act)])

        self.scheduleTable.setItem(0, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Sunday)))
        self.scheduleTable.setItem(1, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Monday)))
        self.scheduleTable.setItem(2, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Tuesday)))
        self.scheduleTable.setItem(3, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Wednesday)))
        self.scheduleTable.setItem(4, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Thursday)))
        self.scheduleTable.setItem(5, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Friday)))
        self.scheduleTable.setItem(6, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Saturday)))
        self.updateDescription(self.shutdownData, self.restartData)

    def isDatetimeWithinThisWeek(self, inputTime):
        todayStr = ""
        nextWeekStr = ""
        now = datetime.datetime.now()
        today = now.date()
        count = 0
        if inputTime.date() == today:
            todayStr = " (Today)"
        else:
            currentWeek = systemFunction.getCurrentWeek()
            if inputTime > currentWeek[6]:  # 時間 > 當週最末一日時間, 表示為下週或下下週
                while inputTime > now:
                    now += datetime.timedelta(7)
                    count += 1

        if count > 0:
            for i in range(count, 0, -1):
                nextWeekStr += "next "

        return (todayStr, nextWeekStr)

    def updatePageByStatus(self, daemonStatus):

        enabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            enabledFlag = False

        elif daemonStatus and daemonStatus.deviceId == -1:
            pass

        elif daemonStatus and daemonStatus.deviceId != -1:
            pass

        for index, item in enumerate(settings.week):
            self.onDDL[index].onHourDDL.setEnabled(enabledFlag)
            self.onDDL[index].onMinDDL.setEnabled(enabledFlag)
            self.offDDL[index].offHourDDL.setEnabled(enabledFlag)
            self.offDDL[index].offMinDDL.setEnabled(enabledFlag)
            self.onActionCheck[index].setEnabled(enabledFlag)
            self.offActionCheck[index].setEnabled(enabledFlag)
            self.offNRCheck[index].setEnabled(enabledFlag)


class PeriodDDL(QWidget):
    def __init__(self, onOffFlag, parent=None):
        super(PeriodDDL, self).__init__(parent)

        # colon = QTableWidgetItem(":")
        if onOffFlag:
            self.onHourDDL = serverHHCombo_Start = ComboBox()
        else:
            self.offHourDDL = serverHHCombo_Start = ComboBox()

        serverHHCombo_Start.setProperty('class', 'scheduleHHCls')

        for item in self.ddlHourContent().items():
            serverHHCombo_Start.addItem(item[0], str(item[1]))

        if onOffFlag:
            self.onMinDDL = serverMMCombo_Start = ComboBox()
        else:
            self.offMinDDL = serverMMCombo_Start = ComboBox()
        serverMMCombo_Start.setProperty('class', 'scheduleMMCls')

        for item in self.ddlMinContent().items():
            serverMMCombo_Start.addItem(item[0], str(item[1]))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(serverHHCombo_Start)
        # layout.addWidget(colon)
        layout.addWidget(serverMMCombo_Start)

        self.setLayout(layout)

    def ddlHourContent(self):
        dic = {"AM 12": 0}
        for i in range(1, 12, 1):
            if i < 10:
                key = "AM 0" + str(i)
            else:
                key = "AM " + str(i)

            dic[key] = i

        dic["PM 12"] = 12
        for i in range(13, 24, 1):
            if i < 22:
                key = "PM 0" + str(i - 12)
            else:
                key = "PM " + str(i - 12)

            dic[key] = i

        return dic

    def ddlMinContent(self):
        dic = dict()
        for i in range(0, 60, 5):
            if i < 10:
                key = "0" + str(i)
            else:
                key = str(i)

            dic[key] = i

        return dic
