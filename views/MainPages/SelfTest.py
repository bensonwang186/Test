import os
import sys
import traceback
from functools import partial

from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QMovie, QPainter, QFontMetrics
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QPushButton)

from System import settings
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.Custom import ViewData
from views.MainPages import TemplatePage


class SelfTest(TemplatePage.TemplatePage):
    _doSelfTestSignal = pyqtSignal(object)

    def __init__(self):
        super(SelfTest, self).__init__()
        self.setAccessibleName("selftestpage")
        self.configGroup = None
        self.selfTestMsgLabel = None
        self.selfTestDateLabel = None
        self.selfTestResultLabel = None
        self.selfTestTriggerMsg = None
        self.selfTestBtn = None
        self.lastSelfTestResult = None
        self.init_ui()

    def init_ui(self):
        # <editor-fold desc="Main data fields">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("selfTestQGroupBox")
        self.configGroup.setAccessibleName("selftestpagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel("Self-Test")
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("selftestpagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("selftest.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        self.selfTestMsgLabel = serverLabel_1 = QLabel(self.getTranslateString(i18nId.i18nId().Self_test_helps_ensure_your_UPS_is_working_correctly))
        # 2019/02/23 Kenneth
        self.selfTestMsgLabel .setWordWrap(True)

        hLayout1 = QHBoxLayout()
        self.selfTestDateLabel = serverLabel_2 = QLabel(self.getTranslateString(i18nId.i18nId().Date_of_last_self_test))
        self.selfTestDateLabel.setAccessibleName("selftestdate")
        serverLabel_2.setProperty('class', 'label-LeftCls-1-left')
        serverLabel_2.setWordWrap(True)

        self.selfTestDateValue = QLabel(self.getTranslateString(i18nId.i18nId().Never))
        self.selfTestDateValue.setProperty('class', 'label-LeftCls-1-right')

        hLayout1.addWidget(serverLabel_2)
        hLayout1.addWidget(self.selfTestDateValue)

        hLayout2 = QHBoxLayout()
        self.selfTestResultLabel = serverLabel_3 = QLabel(self.getTranslateString(i18nId.i18nId().Result_of_last_self_test))
        self.selfTestResultLabel.setAccessibleName("selftestpageresult")
        serverLabel_3.setProperty('class', 'label-LeftCls-2-left')
        serverLabel_3.setWordWrap(True)

        self.selfTestResultValue = QLabel(self.getTranslateString(i18nId.i18nId().Unknown))
        self.selfTestResultValue.setProperty('class', 'label-LeftCls-2-right')

        hLayout2.addWidget(serverLabel_3)
        hLayout2.addWidget(self.selfTestResultValue)

        self.selfTestTriggerMsg = serverLabel_4 = QLabel(self.getTranslateString(i18nId.i18nId().Click_button_to_initiate_a_self_test_to_ensure_UPS_working_correctly))
        self.selfTestTriggerMsg.setProperty('class', 'label-LeftCls-3')
        self.selfTestTriggerMsg.setWordWrap(True)

        hLayout3 = QHBoxLayout()
        self.selfTestBtn = QPushButton("Initiate self-test")
        self.selfTestBtn.setAccessibleName("selftestinit")
        self.selfTestBtn.setDefault(True)
        self.selfTestBtn.clicked.connect(partial(self.selfTestClicked))
        self.selfTestBtn.setProperty('class', 'selfTestBtn')
        self.loadingIcon = QTextMovieLabel(self.getTranslateString(i18nId.i18nId().Self_test_is_in_progress_please_wait),
                                           os.path.join(settings.IMAGE_PATH, "icon_loading.gif"))

        self.loadingIcon.hide()
        hLayout3.addWidget(self.selfTestBtn)
        hLayout3.addWidget(self.loadingIcon)
        hLayout3.addStretch(1)

        serverLayout1 = QVBoxLayout()
        serverLayout1.addWidget(serverLabel_1)
        serverLayout1.addLayout(hLayout1)
        serverLayout1.addLayout(hLayout2)
        serverLayout1.addWidget(ViewData.QHLine())
        serverLayout1.addWidget(serverLabel_4)
        serverLayout1.addLayout(hLayout3)
        serverLayout1.setObjectName('selfTestBtn')

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(serverLayout1)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        # serverLayoutAll.setSpacing(0)
        configGroup.setLayout(serverLayoutAll)

        # </editor-fold>

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setObjectName("selfTestMain")
        mainLayout.addWidget(configGroup)
        mainLayout.addStretch(1)

        self.renderText()
        self.setLayout(mainLayout)

    @property
    def doSelfTestSignal(self):
        return self._doSelfTestSignal

    @doSelfTestSignal.setter
    def doSelfTestSignal(self, value):
        self._doSelfTestSignal = value

    def selfTestClicked(self):
        try:
            self.selfTestBtn.setEnabled(False)
            self.loadingIcon.show()
            self._doSelfTestSignal.emit(None)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def isSelfTestProcessing(self, flag):

        # print("view flag: " + str(flag))
        if flag is False:
            self.selfTestBtn.setEnabled(True)
            self.loadingIcon.hide()

    def restoreSelfTest(self, config):
        if config.selfTestResult is not None and config.selfTestTime is not None:
            try:
                format = "%Y/%m/%d %H:%M:%S"
                # datetime.strptime(config.selfTestTime, format)
                self.selfTestDateValue.setText(config.selfTestTime.strftime("%Y/%m/%d %I:%M:%S %p"))
                # self.selfTestDateValue.setText(datetime.strptime(config.selfTestTime, format))
            except Exception:
                traceback.print_exc(file=sys.stdout)
            if config.selfTestResult:
                self.lastSelfTestResult = True
                self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().Passed))
            else:
                self.lastSelfTestResult = False
                self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().Not_passed))

    def updatePageByStatus(self, daemonStatus):

        disabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            self.lastSelfTestResult = None
            self.selfTestDateValue.setText(self.getTranslateString(i18nId.i18nId().none))
            self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().none))

        elif daemonStatus and daemonStatus.deviceId == -1:
            pass

        elif daemonStatus and daemonStatus.deviceId != -1:
            disabledFlag = False

        self.selfTestBtn.setDisabled(disabledFlag)

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Self_Test))
        self.selfTestMsgLabel.setText(
            self.getTranslateString(i18nId.i18nId().Self_test_helps_ensure_your_UPS_is_working_correctly))
        self.selfTestDateLabel.setText(self.getTranslateString(i18nId.i18nId().Date_of_last_self_test))
        self.selfTestResultLabel.setText(self.getTranslateString(i18nId.i18nId().Result_of_last_self_test))
        self.selfTestTriggerMsg.setText(self.getTranslateString(
            i18nId.i18nId().Click_button_to_initiate_a_self_test_to_ensure_UPS_working_correctly))
        self.selfTestBtn.setText(self.getTranslateString(i18nId.i18nId().Initiate_self_test))
        self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Self_test_is_in_progress_please_wait))

        if self.lastSelfTestResult is not None:
            if self.lastSelfTestResult:
                self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().Passed))
            else:
                self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().Not_passed))
        else:
            self.selfTestDateValue.setText(self.getTranslateString(i18nId.i18nId().none))
            self.selfTestResultValue.setText(self.getTranslateString(i18nId.i18nId().none))

class QTextMovieLabel(QLabel):
    def __init__(self, text, fileName):
        QLabel.__init__(self)
        self._text = text
        m = QMovie(fileName)
        m.start()
        self.setMovie(m)

    def setMovie(self, movie):
        QLabel.setMovie(self, movie)
        s=movie.currentImage().size()
        self._movieWidth = s.width()
        self._movieHeight = s.height()

    def paintEvent(self, evt):
        QLabel.paintEvent(self, evt)
        p = QPainter(self)
        p.setFont(self.font())
        x = self._movieWidth + 6
        y = (self.height() + p.fontMetrics().xHeight()) / 2
        p.drawText(x, y, self._text)
        p.end()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(self._movieWidth + 6 + fm.width(self._text),
                self._movieHeight)

    def setText(self, text):
        self._text = text
