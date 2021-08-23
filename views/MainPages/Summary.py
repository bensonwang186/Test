import traceback
from PyQt5 import QtCore, QtWidgets

import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QComboBox, QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView, QPushButton)

from Events.Event import EventID
from System import systemDefine
from Utility.HelpOpener import HelpOpener
from i18n import i18nId, appLocaleData
from views.MainPages import TemplatePage
from Utility import Logger

class Summary(TemplatePage.TemplatePage):
    _setSummaryFilterSignal = pyqtSignal(object)

    def __init__(self):
        super(Summary, self).__init__()

        self.configGroup = None
        self.lastPowerEventLabel = None
        self.powerConditionSumLabel = None
        self.displayLastLabel = None
        self.filterCombox = None
        self.powerTable = None
        self.voltageTable = None
        self.setAccessibleName("summarypage")
        self.lastEvent = None
        Logger.LogIns().logger.info("Init Summary Page")
        self.init_ui()

    @property
    def setSummaryFilterSignal(self):
        return self._setSummaryFilterSignal

    @setSummaryFilterSignal.setter
    def setSummaryFilterSignal(self, value):
        self._setSummaryFilterSignal = value

    def init_ui(self):

        # <editor-fold desc="Summary UI: label & DDL">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("summaryQGroupBox")
        self.configGroup.setAccessibleName("summarypagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = QLabel()
        self.mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setProperty('class', 'qMark')
        qMark.setAccessibleName("summaryhelp")
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("summary.htm"))

        mainTitleLayout.addWidget(self.mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        self.lastPowerEventLabel = QLabel()
        self.lastPowerEventLabel.setProperty('class', 'label-LeftCls')
        self.lastPowerEventDetail = QLabel()
        self.lastPowerEventDetail.setProperty('class', 'label-RightCls')

        self.powerConditionSumLabel = QLabel()
        self.powerConditionSumLabel.setProperty('class', 'serverLabe2_1')
        self.displayLastLabel = QLabel()
        self.displayLastLabel.setProperty('class', 'displayLastLabel')

        self.filterCombox = QComboBox()
        self.filterCombox.setAccessibleName("summaryperiodfilter")
        self.filterCombox.setProperty('class', 'summaryperiodfilter')
        self.filterCombox.addItem("week", 1)
        self.filterCombox.addItem("4 weeks", 4)
        self.filterCombox.addItem("12 weeks", 12)
        self.filterCombox.addItem("24 weeks", 24)
        self.filterCombox.setObjectName("periodSelect")
        self.filterCombox.activated.connect(self.setFilter)
        self.filterCombox.setView(QtWidgets.QListView())

        serverLayout1 = QHBoxLayout()
        serverLayout1.addWidget(self.lastPowerEventLabel)
        serverLayout1.addWidget(self.lastPowerEventDetail)
        serverLayout1.addStretch(1)
        serverLayout1.setContentsMargins(0, 0, 0, 10)
        serverLayout2 = QHBoxLayout()
        serverLayout2.addWidget(self.powerConditionSumLabel)
        serverLayout2.addWidget(self.displayLastLabel)
        serverLayout2.addWidget(self.filterCombox)
        serverLayout2.addStretch(1)
        serverLayout2.setContentsMargins(0, 0, 0, 10)

        # </editor-fold>

        # <editor-fold desc="Table">

        """The with statement is used to wrap the execution of a block with methods defined by a context manager. 
           This allows common try...except...finally usage patterns to be encapsulated for convenient reuse."""

        # <editor-fold desc="設定table相關參數">

        self.powerTable = QTableWidget(4, 3)
        self.powerTable.setObjectName("powerProblemTable")
        self.powerTable.verticalHeader().setVisible(False)
        self.powerTable.setFocusPolicy(0)
        self.powerTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.powerTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.powerTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.powerTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.powerTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.powerTable.setAlternatingRowColors(True)

        # </editor-fold>

        self.powerTable.setItem(0, 0, QTableWidgetItem("Power outage"))
        self.powerTable.setItem(0, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.powerTable.setItem(0, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        self.powerTable.setItem(1, 0, QTableWidgetItem("Under voltage"))
        self.powerTable.setItem(1, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.powerTable.setItem(1, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        self.powerTable.setItem(2, 0, QTableWidgetItem("Over voltage"))
        self.powerTable.setItem(2, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.powerTable.setItem(2, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        self.powerTable.setItem(3, 0, QTableWidgetItem("Invert total:"))
        self.powerTable.setItem(3, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.powerTable.setItem(3, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        layout = QHBoxLayout()
        layout.addWidget(self.powerTable)

        # <editor-fold desc="設定table相關參數">

        self.voltageTable = QTableWidget(3, 3)
        self.voltageTable.setObjectName("voltageRegulTable")
        self.voltageTable.verticalHeader().setVisible(False)
        self.voltageTable.setFocusPolicy(0)
        self.voltageTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.voltageTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.voltageTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.voltageTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.voltageTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.voltageTable.setAlternatingRowColors(True)

        # </editor-fold>
        self.voltageTable.setItem(0, 0, QTableWidgetItem("Boost"))
        self.voltageTable.setItem(0, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.voltageTable.setItem(0, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        self.voltageTable.setItem(1, 0, QTableWidgetItem("Buck"))
        self.voltageTable.setItem(1, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.voltageTable.setItem(1, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        self.voltageTable.setItem(2, 0, QTableWidgetItem("Regular total:"))
        self.voltageTable.setItem(2, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
        self.voltageTable.setItem(2, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
        layout2 = QHBoxLayout()
        layout2.addWidget(self.voltageTable)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(serverLayout1)
        serverLayoutAll.addLayout(serverLayout2)
        serverLayoutAll.addLayout(layout)
        serverLayoutAll.addLayout(layout2)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        serverLayoutAll.setSpacing(0)

        # </editor-fold>

        configGroup.setLayout(serverLayoutAll)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setObjectName("currentStatusMain")
        mainLayout.addWidget(configGroup)

        self.renderText()
        self.setLayout(mainLayout)

    def showEvent(self, QShowEvent):
        self.setFilter()

    def updateSummaryPage(self, data):
        Logger.LogIns().logger.info("Receive data, update Summary Page")
        timeUnit = " " + self.getTranslateString(i18nId.i18nId().time)
        timesUnit = " " + self.getTranslateString(i18nId.i18nId().times)

        for x in range(0, 3):
            self.powerTable.setItem(x, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
            self.powerTable.setItem(x, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))

        for x in range(0, 2):
            self.voltageTable.setItem(x, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
            self.voltageTable.setItem(x, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))

        for item in data[0]:
            if item.powerProblem == EventID.ID_UTILITY_FAILURE.value:
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.powerTable.setItem(0, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.powerTable.setItem(0, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.powerTable.setItem(0, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.powerTable.setItem(0, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.powerTable.setItem(0, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == EventID.ID_UTILITY_TRANSFER_LOW.value:
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.powerTable.setItem(1, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.powerTable.setItem(1, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.powerTable.setItem(1, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.powerTable.setItem(1, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.powerTable.setItem(1, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == EventID.ID_UTILITY_TRANSFER_HIGH.value:
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.powerTable.setItem(2, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.powerTable.setItem(2, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.powerTable.setItem(2, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.powerTable.setItem(2, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.powerTable.setItem(2, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == "InvertTotal":
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.powerTable.setItem(3, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.powerTable.setItem(3, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.powerTable.setItem(3, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.powerTable.setItem(3, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.powerTable.setItem(3, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == EventID.ID_AVR_BOOST_ACTIVE.value:
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.voltageTable.setItem(0, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.voltageTable.setItem(0, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.voltageTable.setItem(0, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.voltageTable.setItem(0, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.voltageTable.setItem(0, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == EventID.ID_AVR_BUCK_ACTIVE.value:
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.voltageTable.setItem(1, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.voltageTable.setItem(1, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.voltageTable.setItem(1, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.voltageTable.setItem(1, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.voltageTable.setItem(1, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))
            elif item.powerProblem == "RegularTotal":
                if item.numberOfTimes > 0:
                    if item.numberOfTimes == 1:
                        self.voltageTable.setItem(2, 1, QTableWidgetItem(str(item.numberOfTimes) + timeUnit))
                    else:
                        self.voltageTable.setItem(2, 1, QTableWidgetItem(str(item.numberOfTimes) + timesUnit))
                else:
                    self.voltageTable.setItem(2, 1, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                if item.amountOfTime > 0:
                    self.voltageTable.setItem(2, 2, QTableWidgetItem(self.amountOfTimeFormat(item.amountOfTime)))
                else:
                    self.voltageTable.setItem(2, 2, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))

        #<editor-fold desc="replace "---" by Never or None">

        for row in range(self.powerTable.rowCount()):
            for column in range(self.powerTable.columnCount()):
                valueStr = self.powerTable.item(row, column).text()

                if valueStr == systemDefine.noneValueStr:
                    if column == 1:
                        self.powerTable.setItem(row, column, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                    elif column == 2:
                        self.powerTable.setItem(row, column, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))

        for row in range(self.voltageTable.rowCount()):
            for column in range(self.voltageTable.columnCount()):
                valueStr = self.voltageTable.item(row, column).text()

                if valueStr == systemDefine.noneValueStr:
                    if column == 1:
                        self.voltageTable.setItem(row, column,
                                                QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Never)))
                    elif column == 2:
                        self.voltageTable.setItem(row, column, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().none)))

        #</editor-fold>

        if data[1] != None:
            self.lastEvent = data[1]
            self.lastPowerEventDetail.setText(self.lastEventFormat(data[1]))

    def restoreFilter(self, value):

        dic = {1: "week", 4: "4 weeks", 12: "12 weeks", 24: "24 weeks"}
        ddlText = dic[value]
        index = self.filterCombox.findText(ddlText, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.filterCombox.setCurrentIndex(index)

    def setFilter(self):
        # config = DataSource.Configuration()
        # config.summaryFilter = int(self.filterCombox.currentData())
        # self._setSummaryFilterSignal.emit(config)
        self._setSummaryFilterSignal.emit(self.filterCombox.currentData())

    def amountOfTimeFormat(self, seconds):
        result = self.getTranslateString(i18nId.i18nId().none)
        if seconds >= 0:
            days, remainder = divmod(seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            spiltChar = ","

            # 因應日本需求判定若語系為日文則不顯示逗號
            # 現在因為還未實作多個國家的語系不知道每個國家對這個時間的格式要求為何
            # 所以先採用此做法，若之後各國家都有自己要求的格式的話則要翻修這邊的程式
            if (appLocaleData.appLocaleRecorder().appLocale == appLocaleData.appLocaleData().ja_JP):
                spiltChar = ""

            result = ""
            if days > 0:
                result += str(days) + " " + self.getTranslateString(i18nId.i18nId().Days) + spiltChar

            if hours > 0:
                result += str(hours) + " " + self.getTranslateString(i18nId.i18nId().hours) + spiltChar

            if minutes > 0:
                result += str(minutes) + " " + self.getTranslateString(i18nId.i18nId().minutes) + spiltChar

            if seconds > 0:
                result += str(seconds) + " " + self.getTranslateString(i18nId.i18nId().seconds)

        return result

    def lastEventFormat(self, event):
        result = ""

        if event is not None:
            timeStr = ""
            if event.CreateTime is not None:
                timeStr = event.CreateTime.strftime('%Y/%m/%d %I:%M:%S %p')

            if event.EventId == EventID.ID_UTILITY_FAILURE.value:
                result += self.getTranslateString(i18nId.i18nId().AC_utility_power_lost_use_battery_power_at_xxxx).replace("xxxx", timeStr)
            elif event.EventId == EventID.ID_UTILITY_TRANSFER_LOW.value:
                result += self.getTranslateString(
                    i18nId.i18nId().AC_utility_power_is_too_low_use_battery_power_at_xxxx).replace("xxxx", timeStr)
            elif event.EventId == EventID.ID_UTILITY_TRANSFER_HIGH.value:
                result += self.getTranslateString(
                    i18nId.i18nId().AC_utility_power_is_too_high_use_battery_power_at_xxxx).replace("xxxx", timeStr)
            elif event.EventId == EventID.ID_AVR_BOOST_ACTIVE.value:
                result += self.getTranslateString(
                    i18nId.i18nId().AC_utility_frequency_failure_use_battery_power_at_xxxx).replace("xxxx", timeStr)
            elif event.EventId == EventID.ID_AVR_BUCK_ACTIVE.value:
                result += self.getTranslateString(
                    i18nId.i18nId().AC_utility_frequency_failure_use_battery_power_at_xxxx).replace("xxxx", timeStr)

        if len(result) > 50:
            newTimeStr = "<br>" + timeStr
            result = result.replace(timeStr, newTimeStr)

        return result

    def updatePageByStatus(self, daemonStatus):

        if daemonStatus and not daemonStatus.isDaemonStarted:
            tdStr = systemDefine.noneValueStr
            self.powerTable.setItem(0, 1, QTableWidgetItem(tdStr))
            self.powerTable.setItem(0, 2, QTableWidgetItem(tdStr))
            self.powerTable.setItem(1, 1, QTableWidgetItem(tdStr))
            self.powerTable.setItem(1, 2, QTableWidgetItem(tdStr))
            self.powerTable.setItem(2, 1, QTableWidgetItem(tdStr))
            self.powerTable.setItem(2, 2, QTableWidgetItem(tdStr))
            self.powerTable.setItem(3, 1, QTableWidgetItem(tdStr))
            self.powerTable.setItem(3, 2, QTableWidgetItem(tdStr))

            self.voltageTable.setItem(0, 1, QTableWidgetItem(tdStr))
            self.voltageTable.setItem(0, 2, QTableWidgetItem(tdStr))
            self.voltageTable.setItem(1, 1, QTableWidgetItem(tdStr))
            self.voltageTable.setItem(1, 2, QTableWidgetItem(tdStr))
            self.voltageTable.setItem(2, 1, QTableWidgetItem(tdStr))
            self.voltageTable.setItem(2, 2, QTableWidgetItem(tdStr))

            self.lastPowerEventDetail.setText("")
        elif daemonStatus and daemonStatus.deviceId == -1:
            self.setFilter()

        elif daemonStatus and daemonStatus.deviceId != -1:
            self.setFilter()

    def renderText(self):
        try:
            self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Power_Problem_Summary))
            self.lastPowerEventLabel.setText(self.getTranslateString(i18nId.i18nId().Last_Power_Event))
            self.powerConditionSumLabel.setText(self.getTranslateString(i18nId.i18nId().Power_Condition_Summary))
            self.displayLastLabel.setText(
                self.getTranslateString(i18nId.i18nId().Display_period) + " " + self.getTranslateString(i18nId.i18nId().Last))

            self.filterCombox.setItemText(0, self.getTranslateString(i18nId.i18nId().week))
            self.filterCombox.setItemText(1, str("4 ") + self.getTranslateString(i18nId.i18nId().weeks))
            self.filterCombox.setItemText(2, str("12 ") + self.getTranslateString(i18nId.i18nId().weeks))
            self.filterCombox.setItemText(3, str("24 ") + self.getTranslateString(i18nId.i18nId().weeks))
            self.powerTable.setHorizontalHeaderLabels([self.getTranslateString(i18nId.i18nId().Power_problem),
                                                       self.getTranslateString(i18nId.i18nId().Number_of_times),
                                                       self.getTranslateString(i18nId.i18nId().Amount_of_time)])

            self.powerTable.setItem(0, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Power_outage)))
            self.powerTable.setItem(1, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Under_Voltage)))
            self.powerTable.setItem(2, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Over_Voltage)))
            self.powerTable.setItem(3, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Invert_total) + ":"))

            self.voltageTable.setHorizontalHeaderLabels([self.getTranslateString(i18nId.i18nId().Voltage_regulation),
                                                         self.getTranslateString(i18nId.i18nId().Number_of_times),
                                                         self.getTranslateString(i18nId.i18nId().Amount_of_time)])

            self.voltageTable.setItem(0, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Boost)))
            self.voltageTable.setItem(1, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Buck)))
            self.voltageTable.setItem(2, 0, QTableWidgetItem(self.getTranslateString(i18nId.i18nId().Regular_total) + ":"))


            if self.lastEvent is not None:
                self.lastPowerEventDetail.setText(self.lastEventFormat(self.lastEvent))

            self.setFilter()

        except Exception:
            traceback.print_exc(file=sys.stdout)


    class EventDispaly:

        def __init__(self, jsonString=None):
            import json
            self._powerProblem = None
            self._numberOfTimes = None
            self._amountOfTime = None
            if jsonString is not None:
                self.__dict__ = json.loads(jsonString)


        @property
        def powerProblem(self):
            return self._powerProblem

        @powerProblem.setter
        def powerProblem(self, value):
            self._powerProblem = value

        @property
        def numberOfTimes(self):
            return self._numberOfTimes

        @numberOfTimes.setter
        def numberOfTimes(self, value):
            self._numberOfTimes = value

        @property
        def amountOfTime(self):
            return self._amountOfTime

        @amountOfTime.setter
        def amountOfTime(self, value):
            self._amountOfTime = value
