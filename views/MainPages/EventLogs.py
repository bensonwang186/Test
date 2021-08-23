import traceback, datetime, os, sys, functools
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, QSize, QRegExp
from PyQt5.QtGui import QPixmap, QRegExpValidator, QIcon
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QDateTimeEdit, QLineEdit, QWidget,
                             QComboBox, QTableWidgetItem, QTableWidget, QAbstractItemView, QHeaderView, QPushButton, QDialog, QGridLayout, QMessageBox)

from System import settings
from Utility.HelpOpener import HelpOpener
from i18n import i18nId, appLocaleData
from views.MainPages import TemplatePage
from views.Custom.ViewData import EventStatusLevel, ErrorCodeEventNumber, QHLine
from Utility import Logger
from functools import partial
from views.Custom import ViewData

class EventLogs(TemplatePage.TemplatePage):
    _setEventFilterSignal = pyqtSignal(object)
    _clearEventLogsSignal = pyqtSignal()

    def __init__(self):
        super(EventLogs, self).__init__()

        self.configGroup = None
        self.eventLevelFilter = None
        self.eventTable = None
        self.setAccessibleName("eventLogsPage")
        self.pageIndex = dict()
        self.isPaging = False

        # ICON
        self.eventCriticalImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_critical.png"))
        self.eventInfoImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_info.png"))
        self.eventOfflineImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_offline.png"))
        self.eventWarningImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_warning.png"))

        self.eventHardwareFaultImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_hardware_fault.png"))
        self.eventHardwareWarningImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_hardware_warning.png"))

        self.eventHardwareFaultGrayImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_hardware_fault_gray.png"))  # for單數行
        self.eventHardwareFaultWhiteImg = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_event_hardware_fault_white.png"))  # for雙數行

        self.init_ui()

    @property
    def setEventFilterSignal(self):
        return self._setEventFilterSignal

    @setEventFilterSignal.setter
    def setEventFilterSignal(self, value):
        self._setEventFilterSignal = value

    @property
    def clearEventLogsSignal(self):
        return self._clearEventLogsSignal

    @clearEventLogsSignal.setter
    def clearEventLogsSignal(self, value):
        self._clearEventLogsSignal = value

    def init_ui(self):
        try:
            self.configGroup = configGroup = QGroupBox("")
            configGroup.setObjectName("eventQGroupBox")
            self.configGroup.setAccessibleName("eventpagegroup")

            mainTitleLayout = QHBoxLayout()
            self.mainTitle = QLabel()
            self.mainTitle.setProperty('class', 'serverLabel_title')

            qMark = QPushButton("")
            qMark.setProperty('class', 'qMark')
            qMark.setAccessibleName("eventhelp")
            qMark.clicked.connect(lambda: HelpOpener().openHelpDco("eventLogs.htm"))

            mainTitleLayout.addWidget(self.mainTitle)
            mainTitleLayout.addWidget(qMark)
            mainTitleLayout.setProperty('class', 'main_title')

            hLayout2 = QHBoxLayout()
            self.label1 = QLabel()
            self.label1.setProperty('class', 'DateQLabel')
            self.label2 = QLabel()
            self.label2.setProperty('class', 'DateQLabel')

            now = datetime.datetime.now()

            self.startDate = startDate = QDateTimeEdit(self)
            startDate.setProperty('class', 'Date')
            startDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
            startDate.setCalendarPopup(True)
            startDate.dateChanged.connect(self.onDateChanged)  # 設endDateEdit最小值
            startDate.setDisplayFormat("yyyy-MM-dd")
            startDate.setAccessibleName("startdate")

            self.endDate = endDate = QDateTimeEdit(self)
            endDate.setProperty('class', 'Date')
            endDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
            endDate.setCalendarPopup(True)
            endDate.dateChanged.connect(self.onDateChanged)  # 設endDateEdit最小值
            endDate.setDisplayFormat("yyyy-MM-dd")
            endDate.setAccessibleName("enddate")

            self.eventLevelFilter = QComboBox()
            self.eventLevelFilter.setAccessibleName("eventperiodfilter")
            self.eventLevelFilter.setProperty('class', 'eventperiodfilter')
            self.eventLevelFilter.setObjectName("periodSelect")
            self.eventLevelFilter.activated.connect(functools.partial(self.setFilter, False))
            self.eventLevelFilter.setView(QtWidgets.QListView())

            self.searchInput = QLineEdit("")
            self.searchInput.setProperty('class', 'searchInput')
            self.searchInput.textChanged.connect(functools.partial(self.setFilter, False))
            self.searchInput.setClearButtonEnabled(True)

            hLayout2.addWidget(self.label1)
            hLayout2.addWidget(startDate)
            hLayout2.addWidget(self.label2)
            hLayout2.addWidget(endDate)
            hLayout2.addStretch(1)
            hLayout2.setContentsMargins(0, 0, 0, 5)
            hLayout2.addWidget(self.eventLevelFilter)
            hLayout2.addWidget(self.searchInput)

            # self.eventTable = QTableWidget(0, 3)
            self.eventTable = TableWidget(0, 3, self)
            self.eventTable.table.setFixedWidth(570)
            self.eventTable.table.setColumnWidth(0, 40)
            self.eventTable.table.setColumnWidth(1, 160)
            self.eventTable.table.setColumnWidth(2, 350)
            self.eventTable.table.horizontalHeader().setStretchLastSection(True)
            self.eventTable.table.setWordWrap(True)
            self.eventTable.table.setTextElideMode(QtCore.Qt.ElideNone)
            self.eventTable.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.eventTable.table.setObjectName("eventLogsTable")
            self.eventTable.table.setProperty('class', 'en_eventLogsEmpty')
            self.eventTable.table.verticalHeader().setVisible(False)
            self.eventTable.table.setFocusPolicy(0)
            self.eventTable.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.eventTable.table.setSelectionMode(QAbstractItemView.NoSelection)
            self.eventTable.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.eventTable.setContentsMargins(0, 0, 0, 0)
            # self.eventTable.setAlternatingRowColors(True)

            self.eventTable.setPageController(0) # add pagination
            layout = QHBoxLayout()
            layout.addWidget(self.eventTable)


            # clear all btn
            # self.clearAllLabel = QLabel(self.getTranslateString(i18nId.i18nId().clear_all_events))
            # self.clearAllLabel.setProperty('class', 'label-LeftCls-3')
            # self.clearAllLabel.setWordWrap(True)

            # hLayout3 = QHBoxLayout()
            # self.clearAllBtn = QPushButton("")
            # self.clearAllBtn.setAccessibleName("selftestinit")
            # self.clearAllBtn.setDefault(True)
            # self.clearAllBtn.clicked.connect(partial(self.clearAllLogs))
            # self.clearAllBtn.setProperty('class', 'btn clearAllLogs')
            #
            # hLayout3.addWidget(self.clearAllBtn)
            # hLayout3.addStretch(1)
            #
            # vBoxLayout = QVBoxLayout()
            # vBoxLayout.addWidget(QHLine())
            # vBoxLayout.addWidget(self.clearAllLabel)
            # vBoxLayout.addLayout(hLayout3)
            # vBoxLayout.setObjectName('clearBtn')

            serverLayoutAll = QVBoxLayout()
            serverLayoutAll.addLayout(mainTitleLayout)
            serverLayoutAll.addLayout(hLayout2)
            serverLayoutAll.addLayout(layout)
            # serverLayoutAll.addLayout(vBoxLayout)
            serverLayoutAll.setContentsMargins(20, 20, 20, 10)

            configGroup.setLayout(serverLayoutAll)
            mainLayout = QHBoxLayout()
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.setObjectName("currentStatusMain")
            mainLayout.addWidget(configGroup)

            self.renderText()
            self.setLayout(mainLayout)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def showEvent(self, QShowEvent):
        now = datetime.datetime.now()
        self.startDate.clearMaximumDate()
        self.startDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.startDate.setMaximumDate(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.endDate.clearMaximumDate()
        self.endDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.endDate.setMaximumDate(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.setFilter(False)

    def onDateChanged(self):
        self.endDate.setMinimumDate(self.startDate.date().toPyDate())
        self.setFilter(False)

    def clearTable(self):
        self.eventTable.table.clearContents()
        self.eventTable.table.setRowCount(0)  # clear table
        self.eventTable.table.setProperty('class', 'en_eventLogsEmpty')
        self.eventTable.table.style().polish(self.eventTable.table)
        self.eventTable.table.setSortingEnabled(False)

    def updatePage(self, logs, pageIndex):
        try:
            self.eventTable.table.clearContents()
            self.eventTable.table.setRowCount(0)  # clear table
            self.eventTable.table.setSortingEnabled(False)

            if pageIndex is None or pageIndex == {}:  # if result is empty
                self.eventTable.totalPageValue = 0
                self.eventTable.curPage.setText(str(0))

                regex = QRegExp("^[0-9]*[1-9][0-9]*$") # 正整數
                validator = QRegExpValidator(regex)
                self.eventTable.curPage.setValidator(validator)
            else:
                self.pageIndex = pageIndex
                self.eventTable.totalPageValue = int(list(pageIndex)[-1]) # Find the last page no. and save.

                if self.eventTable.currentPageValue == 0:  # empty result -> non-empty result
                    self.eventTable.currentPageValue = 1 # 回第一頁(最新頁)

                self.eventTable.curPage.setText(str(self.eventTable.currentPageValue))

                regex = QRegExp("^[0-9]*[1-9][0-9]*$") # 正整數
                validator = QRegExpValidator(regex)
                self.eventTable.curPage.setValidator(validator)

            self.eventTable.totalPage.setText("/" + str(self.eventTable.totalPageValue))
            self.eventTable.pageNavigatorCtl()

            length = len(logs)
            if length > 0:

                self.eventTable.table.setRowCount(length)
                self.eventTable.table.setColumnCount(3)
                self.eventTable.table.setProperty('class', None)
                self.eventTable.table.style().polish(self.eventTable.table)

                for index,item in enumerate(logs):
                    icon = QLabel(str(index))
                    if "hwFlag" in item and item["hwFlag"] is int(True):

                        if item["id"] == ErrorCodeEventNumber.ID_HARDWARE_STATUS_RESTORE.value:
                            icon.setPixmap(self.eventInfoImg)
                        else:
                            style = ""
                            if "clCode" in item.keys():
                                style = "QLabel { background-color : " + item["clCode"] + "; }"
                            else:
                                style = "QLabel { background-color : #777777; }"

                            icon.setStyleSheet(style)
                            # if index % 2 == 0:  # 雙數行
                            #     icon.setPixmap(self.eventHardwareFaultWhiteImg)
                            # else:  # 單數行
                            #     icon.setPixmap(self.eventHardwareFaultGrayImg)
                            icon.setPixmap(self.eventHardwareFaultWhiteImg)

                    else:
                        if item["lv"] == EventStatusLevel.Normal.value:
                            icon.setPixmap(self.eventInfoImg)
                        elif item["lv"] == EventStatusLevel.Waring.value:
                            icon.setPixmap(self.eventWarningImg)
                        elif item["lv"] == EventStatusLevel.Critical.value:
                            icon.setPixmap(self.eventCriticalImg)
                        elif item["lv"] == EventStatusLevel.Offline.value:
                            icon.setPixmap(self.eventOfflineImg)

                    # icon.setFixedWidth(17)
                    # icon.setFixedHeight(17)
                    icon.setAlignment(QtCore.Qt.AlignCenter)
                    icon.setProperty('class', 'status_icon')
                    self.eventTable.table.setCellWidget(index, 0, icon)
                    # 20201218 Kenneth讓文字靠上
                    timeItem = QTableWidgetItem(item["time"])
                    timeItem.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
                    self.eventTable.table.setItem(index, 1, timeItem)

                    key = "eventId_" + str(item["id"])

                    desc = ""
                    if hasattr(i18nId.i18nId(), key):
                        desc = self.getTranslateString(getattr(i18nId.i18nId(), key))

                    if "hwFlag" in item and item["hwFlag"] is int(True):
                        subKey = "eventCode_" + item["errCode"]
                        if hasattr(i18nId.i18nId(), subKey):
                            desc += ":" + item["errCode"] + ", " + self.i18nTranslater.getTranslateString(getattr(i18nId.i18nId(), subKey))
                    # 20201218 Kenneth讓文字靠上
                    descItem = QTableWidgetItem(desc)
                    descItem.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
                    self.eventTable.table.setItem(index, 2, descItem)

                # self.eventTable.table.setSortingEnabled(True)
                self.eventTable.table.sortItems(1, QtCore.Qt.DescendingOrder)
                self.eventTable.table.setSortingEnabled(True)
            else:
                locale = appLocaleData.appLocaleRecorder().appLocale

                self.eventTable.table.setProperty('class', None)  # clear class

                if hasattr(appLocaleData.appLocaleData(), locale):
                    self.eventTable.table.setProperty('class', (locale + '_eventLogsEmpty'))
                else:
                    self.eventTable.table.setProperty('class', (appLocaleData.appLocaleData().en_US + '_eventLogsEmpty'))

                self.eventTable.table.style().polish(self.eventTable.table)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def setFilter(self, paging):

        try:
            startDate = self.startDate.dateTime().toPyDateTime()
            endDate = self.endDate.dateTime().toPyDateTime()
            lv = self.eventLevelFilter.currentData()
            queryStr = self.searchInput.text()
            limitId = None
            self.isPaging = paging

            if paging is True: # 按下分頁
                isLastPage = self.eventTable.currentPageValue == self.eventTable.totalPageValue
                self.isLastPage = isLastPage

                if self.eventTable.currentPageValue > 0 and len(self.pageIndex) > 0:
                    self.eventTable.curPage.setText(str(self.eventTable.currentPageValue))
                    if str(self.eventTable.currentPageValue) in self.pageIndex.keys():
                        limitId = self.pageIndex[str(self.eventTable.currentPageValue)]
            else:  # 重新搜尋時isPaging必為False, 頁數要導到最新一頁(第一頁)
                self.eventTable.currentPageValue = 1

            self._setEventFilterSignal.emit((startDate, endDate, lv, queryStr, self.eventTable.pageLimit, paging, self.eventTable.currentPageValue, limitId))

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())


    def updatePageByStatus(self, daemonStatus):

        disabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            self.clearTable()
        elif daemonStatus and daemonStatus.deviceId == -1:
            disabledFlag = False
            self.setFilter(False)

        elif daemonStatus and daemonStatus.deviceId != -1:
            disabledFlag = False
            self.setFilter(False)

        self.searchInput.setDisabled(disabledFlag)
        self.eventLevelFilter.setDisabled(disabledFlag)
        self.startDate.setDisabled(disabledFlag)
        self.endDate.setDisabled(disabledFlag)

    def renderText(self):
        try:
            self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Event_Logs))
            self.label1.setText(self.getTranslateString(i18nId.i18nId().From))
            self.label2.setText(self.getTranslateString(i18nId.i18nId().To))

            self.eventLevelFilter.clear()
            self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().All), None)
            self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().Normal), 0)
            self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().Warning), 1)
            self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().Critical), 2)
            self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().hardware_status), -1)
            # self.eventLevelFilter.addItem(self.getTranslateString(i18nId.i18nId().Offline), 3)

            self.searchInput.setPlaceholderText(self.getTranslateString(i18nId.i18nId().Search))
            self.eventTable.table.setHorizontalHeaderLabels(["",self.getTranslateString(i18nId.i18nId().Time), self.getTranslateString(i18nId.i18nId().Events)])

            self.setFilter(False)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def clearAllLogs(self, btn):
        try:
            self.confirmDialog = ConfirmDialog(self)
            self.confirmDialog.setFixedSize(400, 240)
            self.confirmDialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().clear_all_btn))
            self.confirmDialog.exec()
            self.confirmDialog.deleteLater()

            # self.eventTable.curPage.setText(str(0))
            # self.eventTable.currentPageValue = 0
        except Exception:
            traceback.print_exc(file=sys.stdout)

class ConfirmDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        try:
            icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_delete_alert.png"), "alert_imgBox", self)
            icon.setFixedHeight(80)

            hLayout = QHBoxLayout()
            self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Cancel))
            cancelBtn.setProperty('class', 'cancelBtn')
            cancelBtn.clicked.connect(partial(self.dialogCancelClick, parent))
            cancelBtn.setAutoDefault(False)
            # self.cancelBtn.setFixedSize(QSize(80, 32))
            self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
            okBtn.clicked.connect(partial(self.dialogOkClick, parent))  # parent = Advanced class
            okBtn.setAutoDefault(False)
            # self.okBtn.setFixedSize(QSize(80, 32))
            hLayout.addWidget(cancelBtn)
            hLayout.addWidget(okBtn)
            hLayout.addStretch(1)

            termsQLabel = QLabel()
            termsQLabel.setOpenExternalLinks(True)
            termsQLabel.setText(parent.getTranslateString(i18nId.i18nId().are_you_sure_to_delete_all_event_logs))
            termsQLabel.setWordWrap(True)
            termsQLabel.setProperty('class', 'noticeLabel')

            layout = QGridLayout()
            layout.setObjectName("QGridBox")
            layout.addWidget(termsQLabel, 2, 1)

            vlayout = QVBoxLayout(self)
            vlayout.addWidget(icon)
            vlayout.addLayout(layout)
            vlayout.addLayout(hLayout)
            vlayout.setContentsMargins(10, 0, 10, 0)
            # vlayout.addStretch(1)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def closeEvent(self, event):
        self.cancelBtn.click()

    def dialogCancelClick(self, parent):
        self.reject()

    def dialogOkClick(self, parent):
        try:
            parent.clearEventLogsSignal.emit()
        except Exception:
            traceback.print_exc(file=sys.stdout)

class NoticeDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        try:
            icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_delete_alert.png"), "alert_imgBox", self)
            icon.setFixedHeight(80)

            hLayout = QHBoxLayout()
            # self.cancelBtn.setFixedSize(QSize(80, 32))
            self.okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
            self.okBtn.clicked.connect(self.dialogOkClick)
            self.okBtn.setAutoDefault(False)
            # self.okBtn.setFixedSize(QSize(80, 32))
            hLayout.addWidget(self.okBtn)
            # hLayout.addStretch(1)

            termsQLabel = QLabel()
            termsQLabel.setOpenExternalLinks(True)
            termsQLabel.setText(parent.getTranslateString(i18nId.i18nId().input_page_number_is_out_of_range))
            termsQLabel.setWordWrap(True)
            termsQLabel.setProperty('class', 'noticeLabel')

            layout = QGridLayout()
            layout.setObjectName("QGridBox")
            layout.addWidget(termsQLabel, 2, 1)

            vlayout = QVBoxLayout(self)
            vlayout.addWidget(icon)
            vlayout.addLayout(layout)
            vlayout.addLayout(hLayout)
            vlayout.setContentsMargins(10, 0, 10, 0)
            # vlayout.addStretch(1)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def closeEvent(self, event):
        self.okBtn.click()

    def dialogOkClick(self):
        self.reject()

class TableWidget(QWidget):

    def __init__(self, rows, columns, parent=None):
        super(TableWidget, self).__init__()
        self.__init_ui(rows, columns, parent)

    def __init_ui(self, rows, columns, parent):
        self.table = QTableWidget(rows, columns)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.table)
        self.__layout.setContentsMargins(0, 10, 0, 10)
        self.setLayout(self.__layout)
        self.lastTotalPageValue = 0
        self.totalPageValue = 0
        self.currentPageValue = 0
        self.pageLimit = 10
        self.parent = parent

    def setPageController(self, page):
        self.totalPageValue = page
        control_layout = QHBoxLayout()

        self.homePage = QPushButton("")
        self.homePage.setProperty('class', 'btn first_page')

        self.prePage = QPushButton("")
        self.prePage.setProperty('class', 'btn chevron_left')

        self.curPage = QLineEdit()
        self.curPage.setText(str(page))
        self.curPage.setProperty('class', 'pageInput')

        self.totalPage = QLabel("/" + str(self.totalPageValue))
        self.nextPage = QPushButton("")
        self.nextPage.setProperty('class', 'btn chevron_right')

        self.finalPage = QPushButton("")
        self.finalPage.setProperty('class', 'btn last_page')

        self.homePage.clicked.connect(self.__home_page)
        self.prePage.clicked.connect(self.__pre_page)
        self.curPage.textEdited.connect(self.__cur_Page)
        self.nextPage.clicked.connect(self.__next_page)
        self.finalPage.clicked.connect(self.__final_page)

        self.perPageItems = QComboBox()
        self.perPageItems.addItem(str(10), 10)
        self.perPageItems.addItem(str(15), 15)
        self.perPageItems.addItem(str(20), 20)
        # self.perPageItems.setEnabled(False)
        # self.perPageItems.setProperty('class', 'disabled')
        self.perPageItems.activated.connect(self.__per_page_items)
        self.perPageItems.setView(QtWidgets.QListView())

        self.clearAllBtn = QPushButton("")
        self.clearAllBtn.setAccessibleName("selftestinit")
        self.clearAllBtn.setDefault(True)
        self.clearAllBtn.clicked.connect(partial(self.parent.clearAllLogs))
        self.clearAllBtn.setProperty('class', 'btn clearAllLogs')
        # self.clearAllBtn.setEnabled(False)
        # self.clearAllBtn.setProperty('class', 'btn clearAllLogs disabled')

        control_layout.addStretch(0)
        control_layout.addWidget(self.perPageItems)
        control_layout.addWidget(self.homePage)
        control_layout.addWidget(self.prePage)
        control_layout.addWidget(self.curPage)
        control_layout.addWidget(self.totalPage)
        control_layout.addWidget(self.nextPage)
        control_layout.addWidget(self.finalPage)
        control_layout.addWidget(self.clearAllBtn)
        control_layout.addStretch(1)
        self.__layout.addWidget(QHLine())
        self.__layout.addLayout(control_layout)

    def __home_page(self):
        self.curPage.setText(str(1))
        self.currentPageValue = 1
        self.parent.setFilter(True)

    def __pre_page(self):
        self.currentPageValue = int(self.curPage.text())
        if self.currentPageValue in [0, 1]:
            return
        self.currentPageValue -= 1
        self.curPage.setText(str(self.currentPageValue))
        self.parent.setFilter(True)

    def __next_page(self):
        self.currentPageValue = int(self.curPage.text())
        if self.currentPageValue in [0, self.totalPageValue]:
            return
        self.currentPageValue += 1
        self.curPage.setText(str(self.currentPageValue))
        self.parent.setFilter(True)

    def __final_page(self):
        self.currentPageValue = self.totalPageValue
        self.curPage.setText(str(self.totalPageValue))
        self.parent.setFilter(True)

    def __per_page_items(self):
        self.pageLimit = self.perPageItems.currentData()
        self.parent.setFilter(False)  # update page index

    def __cur_Page(self):
        if len(self.curPage.text()) > 0:
            pageValue = int(self.curPage.text())

            if 0 < pageValue <= self.totalPageValue:
                self.currentPageValue = pageValue
                self.parent.setFilter(True)
            else:
                self.NoticeDialog = NoticeDialog(self.parent)
                self.NoticeDialog.setFixedSize(400, 240)
                self.NoticeDialog.setWindowTitle(self.parent.getTranslateString(i18nId.i18nId().notice))
                self.NoticeDialog.exec()
                self.NoticeDialog.deleteLater()

    def pageNavigatorCtl(self):

        if self.totalPageValue >= 2:
            self.homePreCtl(True)
            self.nextFinalCtl(True)

            if self.currentPageValue == self.totalPageValue:
                self.nextFinalCtl(False)
            else:
                if self.currentPageValue == 1:
                    self.homePreCtl(False)
        else:
            self.homePreCtl(False)
            self.nextFinalCtl(False)

    def homePreCtl(self, enableFlag):

        cls1 = 'btn first_page'
        cls2 = 'btn chevron_left'
        if enableFlag is False:
            cls1 += ' disabled'
            cls2 += ' disabled'

        self.homePage.setEnabled(enableFlag)
        self.homePage.setProperty('class', cls1)
        self.homePage.style().polish(self.homePage)

        self.prePage.setEnabled(enableFlag)
        self.prePage.setProperty('class', cls2)
        self.prePage.style().polish(self.prePage)

    def nextFinalCtl(self, enableFlag):

        cls1 = 'btn chevron_right'
        cls2 = 'btn last_page'
        if enableFlag is False:
            cls1 += ' disabled'
            cls2 += ' disabled'

        self.nextPage.setEnabled(enableFlag)
        self.nextPage.setProperty('class', cls1)
        self.nextPage.style().polish(self.nextPage)

        self.finalPage.setEnabled(enableFlag)
        self.finalPage.setProperty('class', cls2)
        self.finalPage.style().polish(self.finalPage)




