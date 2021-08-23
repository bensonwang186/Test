import os
import re
import sys
import traceback

from IPy import IP
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QIntValidator, QMovie, QPainter, QFontMetrics
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QWidget, QFrame, QRadioButton, QCheckBox, QLineEdit,
                             QPushButton, QScrollArea, QButtonGroup)

from System import settings
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from model_Json import DataSource2
from model_Json.tables.EmailNotification import EmailNotification
from views.Custom import ViewData
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox

ERROR_MSG_STYLE = "color: #db232b; margin-top: 10px;"
SUCCESS_MSG_STYLE = "color: #1b44e8; margin-top: 10px;"

CONNECT_TLS = "TLS"
CONNECT_SSL = "SSL"
CONNECT_NONE = "None"
DEFAULT_TLS_PORT_MESG = "Default port 587"
DEFAULT_SSL_PORT_MESG = "Default port 465"
DEFAULT_NONE_PORT_MESG = "Default port 25"


class Notification(TemplatePage.TemplatePage):
    # alarm signal
    _setNotificationSignal = pyqtSignal(object)

    # email signal
    _setNotificationSignal = pyqtSignal(object)
    _oathRequestSignal = pyqtSignal(object)
    _oathExchangedSignal = pyqtSignal(object)
    _refreshSignal = pyqtSignal(object)
    _sendTestEmailSignal = pyqtSignal(object)
    _setUPSAlarmSignal = pyqtSignal(object)
    _setSoftSoundSignal = pyqtSignal(object)
    verifyEmailSettingSignal = pyqtSignal()

    def __init__(self, masterPage):
        super(Notification, self).__init__()
        self.setAccessibleName("notificationpage")
        self.isTesting = False
        self.isVerifying = False
        self.isOauthing = False

        self.masterPage = masterPage

        self.configGroup = None
        self.softTitleLable = None
        self.softMsgLabel = None
        self.softCheckBox = None
        self.upsAlarmTitleLabel = None
        self.upsAlarmMsgLabel = None
        self.alarmEnableRadioBtn = None
        self.alarmDisableRadioBtn = None
        self.activeB1 = None
        self.activeB2 = None
        self.serviceDDL = None
        self.smtpAddrEdit = None
        self.secB1 = None
        self.secB2 = None
        self.secB3 = None
        self.secConnectTip = None
        self.servicePortEdit = None
        self.senderNameEdit = None
        self.senderEmailAddress = None
        self.authB1 = None
        self.authB2 = None
        self.authPasswordEdit = None
        self.authAccountEdit = None
        self.receiverEdit = None

        self.authorizeBtn = None
        self.testBtn = None
        self.verifyBtn = None
        self.applyBtn = None

        # email frame
        self.activeFrame = None
        self.serviceProviderFrame = None
        self.smtpServerAddressFrame = None
        self.secureConnFrame = None
        self.servicePortFrame = None
        self.senderNameFrame = None
        self.senderAddressFrame = None
        self.needAuthFrame = None
        self.authAccountFrame = None
        self.authPasswordFrame = None
        self.receiverFrame = None

        self.OAuthExchangeResultLabel = None

        self.mailLabelOAuth = None
        self.authedLabel = None
        self.authorizeBtn = None

        self.errorMsg = None
        self.isOauthed = False

        self.loadingIcon = None
        self.daemonStatusFlag = False
        self.init_ui()

    @property
    def setNotificationSignal(self):
        return self._setNotificationSignal

    @setNotificationSignal.setter
    def setNotificationSignal(self, value):
        self._setNotificationSignal = value

    @property
    def setSoftSoundSignal(self):
        return self._setSoftSoundSignal

    @setSoftSoundSignal.setter
    def setSoftSoundSignal(self, value):
        self._setSoftSoundSignal = value

    @property
    def oathRequestSignal(self):
        return self._oathRequestSignal

    @oathRequestSignal.setter
    def oathRequestSignal(self, value):
        self._oathRequestSignal = value

    @property
    def oathExchangedSignal(self):
        return self._oathExchangedSignal

    @oathExchangedSignal.setter
    def oathExchangedSignal(self, value):
        self._oathExchangedSignal = value

    @property
    def refreshSignal(self):
        return self._refreshSignal

    @refreshSignal.setter
    def refreshSignal(self, value):
        self._refreshSignal = value

    @property
    def sendTestEmailSignal(self):
        return self._sendTestEmailSignal

    @sendTestEmailSignal.setter
    def sendTestEmailSignal(self, value):
        self._sendTestEmailSignal = value

    @property
    def setUPSAlarmSignal(self):
        return self._setUPSAlarmSignal

    @setUPSAlarmSignal.setter
    def setUPSAlarmSignal(self, value):
        self._setUPSAlarmSignal = value

    def init_ui(self):

        # <editor-fold desc="Current Status UI: Main data fields">

        self.configGroup = configGroup = QGroupBox("")

        # globaWidget is solve radio button grouping problem, keyword: QRadioButton QGroupButton
        self.globalWidget = QWidget(self)
        configGroup.setObjectName("notificationQGroupBox")
        self.configGroup.setAccessibleName("notificationpagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel("Notification")
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("notificationpagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("notification.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')
        # 取消標題與問號間距
        mainTitleLayout.addStretch(1)
        mainTitleLayout.setSpacing(0)
        mainTitleLayout.setContentsMargins(0, 0, 0, 0)

        # <editor-fold desc="Software Sounds">

        self.softTitleLable = label_1 = QLabel("Software Sounds")
        label_1.setProperty('class', 'label-LeftCls')
        self.softMsgLabel = label_2 = QLabel("PowerPanel generates audible sounds to notify you of power events.")

        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(label_1)
        vLayout1.addWidget(label_2)
        self.softCheckBox = QCheckBox("Enbale PowerPanel notification sounds.")
        self.softCheckBox.setAccessibleName("notificationpagesoftwaresoundselect")
        self.softCheckBox.clicked.connect(lambda: self.softwareSoundCheck(self.softCheckBox))
        vLayout1.addWidget(self.softCheckBox)

        # </editor-fold>

        # <editor-fold desc="UPS Alarms">
        self.upsAlarmTitleLabel = label_40 = QLabel("UPS Alarms")
        label_40.setProperty('class', 'label-LeftCls')
        self.upsAlarmMsgLabel = label_4 = QLabel("The UPS generates audible alarms during power events.")

        self.alarmEnableRadioBtn = QRadioButton()
        self.alarmEnableRadioBtn.setAccessibleName("notificationpageenablealarms")
        self.alarmEnableRadioBtn.clicked.connect(lambda: self.enableAlarm(self.alarmEnableRadioBtn.isChecked()))
        #self.alarmEnableRadioBtn.setFixedWidth(161)
        self.alarmDisableRadioBtn = QRadioButton()
        self.alarmDisableRadioBtn.setAccessibleName("notificationpagedisablealarms")
        self.alarmDisableRadioBtn.clicked.connect(lambda: self.enableAlarm(self.alarmEnableRadioBtn.isChecked()))
        #self.alarmDisableRadioBtn.setFixedWidth(166)
        # self.alarmDisableRadioBtn.toggled.connect(lambda: self.enableAlarm(0))

        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(label_40)
        vLayout2.addWidget(label_4)
        vLayout2.addWidget(self.alarmEnableRadioBtn)
        vLayout2.addWidget(self.alarmDisableRadioBtn)

        # </editor-fold>

        # <editor-fold desc="E-mail">

        self.label_5 = QLabel()
        self.label_5.setProperty('class', 'label-LeftCls')


        mailHLayout0 = QVBoxLayout()
        mailHLayout0.addWidget(self.label_5)

        #  ----------------------分隔線----------------------
        self.activeFrame = QFrame(self.globalWidget)
        self.activeFrame.setContentsMargins(0, 0, 0, 0)
        mailHLayout1 = QHBoxLayout()
        self.mailLabel1 = QLabel()
        self.mailLabel1.setProperty('class', 'Email-label-LeftCls')
        self.activeB1 = QRadioButton()
        self.activeB1.setAccessibleName("notificationpageemailactivateyes")
        self.activeB1.setChecked(False)
        self.activeB1.toggled.connect(self.emailSettingsChange)

        self.activeB2 = QRadioButton()
        self.activeB2.setAccessibleName("notificationpageemailactivateno")
        self.activeB2.setChecked(True)
        self.activeB2.toggled.connect(self.emailSettingsChange)
        activeBuutonGroup = QButtonGroup(self.globalWidget)
        activeBuutonGroup.addButton(self.activeB1)
        activeBuutonGroup.addButton(self.activeB2)
        mailHLayout1.addWidget(self.mailLabel1)
        mailHLayout1.addWidget(self.activeB1)
        mailHLayout1.addWidget(self.activeB2)
        mailHLayout1.addStretch(1)
        self.activeFrame.setLayout(mailHLayout1)
        mailHLayout1.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.serviceProviderFrame = QFrame(self.globalWidget)
        mailHLayout2 = QHBoxLayout()
        self.mailLabel2 = QLabel()
        self.mailLabel2.setProperty('class', 'Email-label-LeftCls')
        self.serviceDDL = ComboBox()
        self.serviceDDL.setAccessibleName("notificationpageserviceproviderselect")
        self.serviceDDL.addItem("gmail")
        self.serviceDDL.addItem("Other")
        self.serviceDDL.setProperty('class', 'notificationQCCls')
        self.serviceDDL.setView(QtWidgets.QListView())

        self.serviceDDL.currentIndexChanged.connect(lambda: self.providerChanged(self.serviceDDL.currentIndex()))

        mailHLayout2.addWidget(self.mailLabel2)
        mailHLayout2.addWidget(self.serviceDDL)
        mailHLayout2.addStretch(1)
        self.serviceProviderFrame.setLayout(mailHLayout2)
        mailHLayout2.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.notAuthFrame = QFrame(self.globalWidget)
        mailHLayoutOAuth = QHBoxLayout()
        self.mailLabelOAuth = QLabel()
        self.mailLabelOAuth.setProperty('class', 'notificationpageoauthedit')
        self.oauthCodeEdit = QLineEdit("")
        self.oauthCodeEdit.setAccessibleName("notificationpageoauthedit")
        self.oauthCodeEdit.hide()
        self.oauthStep1 = QPushButton()
        self.oauthStep1.setAccessibleName("notificationpagerequest")
        self.oauthStep1.setProperty('class', 'emailAuthBtn')

        self.oauthStep1.clicked.connect(self.oauthRequest)
        self.oauthCodeEdit.textChanged.connect(lambda: self.oauthTextChanged(self.oauthCodeEdit.text()))

        mailHLayoutOAuth.addWidget(self.mailLabelOAuth)
        mailHLayoutOAuth.addWidget(self.oauthCodeEdit)
        mailHLayoutOAuth.addWidget(self.oauthStep1)
        mailHLayoutOAuth.addStretch(1)
        self.notAuthFrame.setLayout(mailHLayoutOAuth)
        mailHLayoutOAuth.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.authedFrame = QFrame(self.globalWidget)
        mailHLayoutOAuthed = QHBoxLayout()
        self.mailLabelOAuth = QLabel()
        self.mailLabelOAuth.setProperty('class', 'Email-label-LeftCls')

        self.authedLabel = QLabel("")
        self.authedLabel.setProperty('class', 'Email-label-LeftCls')
        self.authedFrame.hide()

        self.authorizeBtn = QPushButton()
        self.authorizeBtn.setAccessibleName("notificationpageemailchange")
        self.authorizeBtn.setProperty('class', 'emailAuthBtn')
        self.authorizeBtn.clicked.connect(self.oauthRequest)
        mailHLayoutOAuthed.addWidget(self.mailLabelOAuth)
        mailHLayoutOAuthed.addWidget(self.authedLabel)
        mailHLayoutOAuthed.addWidget(self.authorizeBtn)
        mailHLayoutOAuthed.addStretch(1)
        mailHLayoutOAuthed.setContentsMargins(0, 0, 0, 0)
        self.authedFrame.setLayout(mailHLayoutOAuthed)
        self.authedFrame.setHidden(True)

        #  ----------------------分隔線----------------------
        self.smtpServerAddressFrame = QFrame(self.globalWidget)
        mailHLayout3 = QHBoxLayout()
        self.mailLabel3 = QLabel()
        self.mailLabel3.setProperty('class', 'Email-label-LeftCls')
        self.smtpAddrEdit = QLineEdit("")
        self.smtpAddrEdit.setAccessibleName("notificationpagesmtpaddredit")
        self.smtpAddrEdit.textChanged.connect(self.emailSettingsChange)
        self.smtpAddrEdit.setProperty('class', 'Email-QLine')
        mailHLayout3.addWidget(self.mailLabel3)
        mailHLayout3.addWidget(self.smtpAddrEdit)
        mailHLayout3.addStretch(1)
        self.smtpServerAddressFrame.setLayout(mailHLayout3)
        mailHLayout3.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.secureConnFrame = QFrame(self.globalWidget)
        mailHLayout4 = QHBoxLayout()
        self.mailLabel4 = QLabel()
        self.mailLabel4.setProperty('class', 'Email-label-LeftCls')
        self.secB1 = QRadioButton(CONNECT_TLS)
        self.secB1.setAccessibleName("notificationpagesecuretls")
        self.secB1.setChecked(True)
        self.secB2 = QRadioButton(CONNECT_SSL)
        self.secB2.setAccessibleName("notificationpagesecuressl")

        self.secB3 = QRadioButton(CONNECT_NONE)
        self.secB3.setAccessibleName("notificationpagesecurenone")

        self.secB1.clicked.connect(lambda: self.secureConnectCheck(self.secB1))
        self.secB2.clicked.connect(lambda: self.secureConnectCheck(self.secB2))
        self.secB3.clicked.connect(lambda: self.secureConnectCheck(self.secB3))

        securityButtonGroup = QButtonGroup(self.globalWidget)
        securityButtonGroup.addButton(self.secB1)
        securityButtonGroup.addButton(self.secB2)
        securityButtonGroup.addButton(self.secB3)
        mailHLayout4.addWidget(self.mailLabel4)
        mailHLayout4.addWidget(self.secB1)
        mailHLayout4.addWidget(self.secB2)
        mailHLayout4.addWidget(self.secB3)
        mailHLayout4.addStretch(1)
        self.secureConnFrame.setLayout(mailHLayout4)
        mailHLayout4.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.servicePortFrame = QFrame(self.globalWidget)
        mailHLayout5 = QHBoxLayout()
        self.mailLabel5 = QLabel("Service port")
        self.mailLabel5.setProperty('class', 'Email-label-LeftCls')
        self.servicePortEdit = QLineEdit("587")
        self.servicePortEdit.setAccessibleName("notificationpageserviceportedit")
        portValidator = QIntValidator()
        portValidator.setRange(0, 65535)
        self.servicePortEdit.setValidator(portValidator)
        self.servicePortEdit.textChanged.connect(self.emailSettingsChange)
        self.secConnectTip = QLabel(DEFAULT_TLS_PORT_MESG)
        mailHLayout5.addWidget(self.mailLabel5)
        mailHLayout5.addWidget(self.servicePortEdit)
        mailHLayout5.addWidget(self.secConnectTip)
        mailHLayout5.addStretch(1)
        self.servicePortFrame.setLayout(mailHLayout5)
        mailHLayout5.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.senderNameFrame = QFrame(self.globalWidget)
        mailHLayout6 = QHBoxLayout()
        self.mailLabel6 = QLabel()
        self.mailLabel6.setProperty('class', 'Email-label-LeftCls')
        self.senderNameEdit = QLineEdit("")
        self.senderNameEdit.setAccessibleName("notificationpagesendernameedit")
        self.senderNameEdit.textChanged.connect(self.emailSettingsChange)
        mailHLayout6.addWidget(self.mailLabel6)
        mailHLayout6.addWidget(self.senderNameEdit)
        mailHLayout6.addStretch(1)
        self.senderNameFrame.setLayout(mailHLayout6)
        mailHLayout6.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.senderAddressFrame = QFrame(self.globalWidget)
        mailHLayout7 = QHBoxLayout()
        self.mailLabel7 = QLabel()
        self.mailLabel7.setProperty('class', 'Email-label-LeftCls')
        self.senderEmailAddress = QLineEdit("")
        self.senderEmailAddress.setAccessibleName("notificationpagesenderemailaddressedit")
        self.senderEmailAddress.textChanged.connect(self.emailSettingsChange)
        self.senderEmailAddress.setProperty('class', 'Email-QLine')
        mailHLayout7.addWidget(self.mailLabel7)
        mailHLayout7.addWidget(self.senderEmailAddress)
        mailHLayout7.addStretch(1)
        self.senderAddressFrame.setLayout(mailHLayout7)
        mailHLayout7.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.needAuthFrame = QFrame(self.globalWidget)
        mailHLayout8 = QHBoxLayout()
        self.mailLabel8 = QLabel()
        self.mailLabel8.setProperty('class', 'Email-label-LeftCls')
        self.authB1 = QRadioButton()
        self.authB1.setAccessibleName("notificationpageauthyes")
        self.authB1.setChecked(False)

        self.authB2 = QRadioButton()
        self.authB2.setAccessibleName("notificationpageauthno")
        self.authB2.setChecked(True)

        self.authB1.clicked.connect(self.emailSettingsChange)
        self.authB2.clicked.connect(self.emailSettingsChange)

        authButtonGroup = QButtonGroup(self.globalWidget)
        authButtonGroup.addButton(self.authB1)
        authButtonGroup.addButton(self.authB2)
        mailHLayout8.addWidget(self.mailLabel8)
        mailHLayout8.addWidget(self.authB1)
        mailHLayout8.addWidget(self.authB2)
        mailHLayout8.addStretch(1)
        self.needAuthFrame.setLayout(mailHLayout8)
        mailHLayout8.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.authAccountFrame = QFrame(self.globalWidget)
        mailHLayout9 = QHBoxLayout()
        self.mailLabel9 = QLabel()
        self.mailLabel9.setProperty('class', 'Email-label-LeftCls')
        self.authAccountEdit = QLineEdit("")
        self.authAccountEdit.setAccessibleName("notificationpageaccountedit")
        self.authAccountEdit.textChanged.connect(self.emailSettingsChange)
        mailHLayout9.addWidget(self.mailLabel9)
        mailHLayout9.addWidget(self.authAccountEdit)
        mailHLayout9.addStretch(1)
        self.authAccountFrame.setLayout(mailHLayout9)
        mailHLayout9.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------

        self.authPasswordFrame = QFrame(self.globalWidget)
        mailHLayout10 = QHBoxLayout()
        self.mailLabel10 = QLabel()
        self.mailLabel10.setProperty('class', 'Email-label-LeftCls')
        self.authPasswordEdit = QLineEdit("")
        self.authPasswordEdit.setAccessibleName("notificationpagepasswordedit")
        self.authPasswordEdit.setEchoMode(QLineEdit.Password)
        self.authPasswordEdit.textChanged.connect(self.emailSettingsChange)
        self.authPasswordEdit.setProperty('class', 'Email-QLine')
        mailHLayout10.addWidget(self.mailLabel10)
        mailHLayout10.addWidget(self.authPasswordEdit)
        mailHLayout10.addStretch(1)
        self.authPasswordFrame.setLayout(mailHLayout10)
        mailHLayout10.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.receiverFrame = QFrame(self.globalWidget)
        mailHLayout11 = QHBoxLayout()
        self.mailLabel11 = QLabel()
        self.mailLabel11.setProperty('class', 'Email-label-LeftCls')
        self.receiverEdit = QLineEdit("")
        self.receiverEdit.setAccessibleName("notificationpagereceiveredit")
        self.receiverEdit.textChanged.connect(self.emailSettingsChange)
        self.testBtn = QPushButton()
        self.testBtn.setAccessibleName("notificationpagetest")
        # self.applyBtn.setDefault(True)
        self.testBtn.clicked.connect(self.sendTestEmail)
        self.testBtn.setProperty('class', 'Email-testBtn')

        mailHLayout11.addWidget(self.mailLabel11)
        mailHLayout11.addWidget(self.receiverEdit)
        mailHLayout11.addWidget(self.testBtn)
        mailHLayout11.addStretch(1)
        self.receiverFrame.setLayout(mailHLayout11)
        mailHLayout11.setContentsMargins(0, 0, 0, 0)

        #  ----------------------分隔線----------------------
        self.loadingIcon = QTextMovieLabel('',
                                           os.path.join(settings.IMAGE_PATH, "icon_loading.gif"))
        mailHLayout11_Error = QHBoxLayout()
        self.errorMsg = QLabel("")
        self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)

        self.loadingIcon.hide()
        mailHLayout11_Error.addWidget(self.loadingIcon)
        mailHLayout11_Error.addWidget(self.errorMsg)

        #  ----------------------分隔線----------------------
        mailHLayout12 = QHBoxLayout()
        self.applyBtn = QPushButton()
        self.applyBtn.setAccessibleName("notificationpageapply")
        # self.applyBtn.setDefault(True)
        self.applyBtn.clicked.connect(lambda: self.whichbtn(self.applyBtn))
        self.applyBtn.setProperty('class', 'Email-applyBtn')

        self.verifyBtn = QPushButton()
        self.verifyBtn.setAccessibleName("notificationpageverify")
        # self.verifyBtn.setDefault(True)
        self.verifyBtn.clicked.connect(self.emailSettingsVerify)
        self.verifyBtn.setProperty('class', 'Email-verifyBtn')
        self.verifyBtn.setDisabled(True)
        mailHLayout12.addWidget(self.applyBtn)
        mailHLayout12.addWidget(self.verifyBtn)
        mailHLayout12.addStretch(1)

        vLayout3 = QVBoxLayout()
        vLayout3.addLayout(mailHLayout0)
        vLayout3.addWidget(self.activeFrame)
        vLayout3.addWidget(self.serviceProviderFrame)
        vLayout3.addWidget(self.notAuthFrame)
        vLayout3.addWidget(self.authedFrame)
        vLayout3.addWidget(self.smtpServerAddressFrame)
        vLayout3.addWidget(self.secureConnFrame)
        vLayout3.addWidget(self.servicePortFrame)
        vLayout3.addWidget(self.senderNameFrame)
        vLayout3.addWidget(self.senderAddressFrame)
        vLayout3.addWidget(self.needAuthFrame)
        vLayout3.addWidget(self.authAccountFrame)
        vLayout3.addWidget(self.authPasswordFrame)
        vLayout3.addWidget(self.receiverFrame)

        vLayout3.addLayout(mailHLayout11_Error)
        vLayout3.addWidget(ViewData.QHLine())
        vLayout3.addLayout(mailHLayout12)
        vLayout3.setProperty('class', 'N_Box3')

        # </editor-fold>

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(vLayout1)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vLayout2)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vLayout3)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        configGroup.setLayout(serverLayoutAll)
        # serverLayoutAll.setSpacing(0)

        # <editor-fold desc="Scroll Area">

        scroll = QScrollArea()
        scroll.setWidget(configGroup)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(450)
        scroll.setFixedWidth(610)
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setHorizontalScrollBarPolicy(1)  # 隱藏X軸卷軸


        # </editor-fold>

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setObjectName("currentStatusMain")
        mainLayout.addWidget(scroll)
        mainLayout.addStretch(1)


        # </editor-fold>


        self.renderText()
        self.setLayout(mainLayout)

    def showEvent(self, QShowEvent):
        # clear message
        self.applyBtn.setDisabled(True)
        self.errorMsg.setText("")
        self.setInputFixedWidth()
        if self.daemonStatusFlag:
            # self.verifyBtn.setDisabled(False)
            # self.testBtn.setDisabled(False)
            # self.applyBtn.setDisabled(True)

            self.decideShow(self.serviceDDL.currentIndex())
            self._refreshSignal.emit(self)

            if self.isVerifying:
                self.clearNotifyMessage()
                self.disabledPage(True)
                self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Verifying))
                self.loadingIcon.show()
                self.isVerifying = True

            if self.isTesting:
                self.clearNotifyMessage()
                self.disabledPage(True)
                self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Testing))
                self.loadingIcon.show()

            if self.isOauthing:
                self.disabledPage(True)
                self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Verifying))
                self.loadingIcon.show()

        else:
            self.verifyBtn.setDisabled(True)
            self.testBtn.setDisabled(True)
            self.applyBtn.setDisabled(True)

    def setInputFixedWidth(self):
        self.smtpAddrEdit.setFixedWidth(200)
        self.servicePortEdit.setFixedWidth(200)
        self.senderNameEdit.setFixedWidth(200)
        self.senderEmailAddress.setFixedWidth(200)
        self.authAccountEdit.setFixedWidth(200)
        self.authPasswordEdit.setFixedWidth(200)
        self.receiverEdit.setFixedWidth(200)
        self.authedLabel.setFixedWidth(200)
        self.oauthCodeEdit.setFixedWidth(200)

    def softwareSoundCheck(self, btn):
        self.setSoftSoundSignal.emit(btn.isChecked())

    def enableAlarm(self, param):
        param = int(param)
        self._setUPSAlarmSignal.emit(param)

    def checkVerifyBtnEnable(self):
        pass

    def toogleExchangedSuccessWidget(self, userAgent):
        self.notAuthFrame.hide()
        self.authedFrame.show()
        self.authedLabel.setText(userAgent)
        self.oauthCodeEdit.clear()

    def oauthTextChanged(self, b):
        self.emailSettingsChange()

        # avoid code is too short, at least need longer than 30
        if len(b) >= 30:
            # todo
            self.oauthVerify()
            self._oathExchangedSignal.emit(b)

    def oauthVerify(self):
        self.disabledPage(True)
        self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Verifying))
        self.loadingIcon.show()

    def oauthVerifyResult(self, result):
        # self.disabledPage(False)
        self.loadingIcon.hide()
        self.activeB1.setDisabled(False)
        self.activeB2.setDisabled(False)
        self.serviceDDL.setDisabled(False)
        self.senderNameEdit.setDisabled(False)
        self.receiverEdit.setDisabled(False)
        self.authorizeBtn.setDisabled(False)
        self.oauthStep1.setDisabled(False)
        self.oauthCodeEdit.setDisabled(False)
        # self._refreshSignal.emit(self)
        if result:
            self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)

            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Exchange_Success))
        else:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Exchange_Failure))

    def sendTestEmail(self):
        self.clearNotifyMessage()
        self.disabledPage(True)
        self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Testing))
        self.loadingIcon.show()
        self.sendTestEmailSignal.emit(self)

    def testingResult(self, result):
        self.loadingIcon.hide()
        self._refreshSignal.emit(self)
        # self.disabledPage(False)

        if result:
            self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Test_Send_Success))
        else:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Test_Send_Failure))

    def isSMTPEditorValid(self):
        try:
            IP(self.smtpAddrEdit.text())
        except Exception:
            if not re.match(r"[^@]+[^@]+", self.smtpAddrEdit.text()):
                return False
        return True

    def isSenderValid(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.senderEmailAddress.text()):
            return False
        return True

    def whichbtn(self, b):
        try:
            self.clearNotifyMessage(False)

            print(self.serviceDDL.currentIndex())
            if self.serviceDDL.currentIndex() == DataSource2.EmailServiceProvider.GMAIL.value:
                emailNotification = EmailNotification()
                emailNotification.active = self.activeB1.isChecked()
                emailNotification.serviceProvider = self.serviceDDL.currentIndex()
                emailNotification.senderName = self.senderNameEdit.text()
                emailNotification.receivers = self.receiverEdit.text()
                self._setNotificationSignal.emit(emailNotification)
                self.applyBtn.setDisabled(True)
                self.verifyBtn.setDisabled(False)
                self.testBtn.setDisabled(False)
                return
        except Exception:
            traceback.print_exc(file=sys.stdout)
        # check SMTP text format
        isIPFormat = False
        smtpAddress = self.smtpAddrEdit.text()

        if not self.isSMTPEditorValid():
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().SMTP_Address_Invalid))
            return

        if not self.isSenderValid():
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Email_Format_error))
            return

        if self.authB1.isChecked() and self.authAccountEdit.text() == "":
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Account_cannot_be_empty_when_auth_active))
            return

        self._setNotificationSignal.emit(self.collectEmailData())
        self.applyBtn.setDisabled(True)
        self.verifyBtn.setDisabled(False)
        self.testBtn.setDisabled(False)
        print("clicked button is " + b.text())

    def disabledPage(self, disabled):
        self.activeB1.setDisabled(disabled)
        self.activeB2.setDisabled(disabled)
        self.serviceDDL.setDisabled(disabled)
        self.smtpAddrEdit.setDisabled(disabled)
        self.secB1.setDisabled(disabled)
        self.secB2.setDisabled(disabled)
        self.secB3.setDisabled(disabled)
        self.servicePortEdit.setDisabled(disabled)
        self.senderNameEdit.setDisabled(disabled)
        self.senderEmailAddress.setDisabled(disabled)
        self.authB1.setDisabled(disabled)
        self.authB2.setDisabled(disabled)
        self.authPasswordEdit.setDisabled(disabled)
        self.authAccountEdit.setDisabled(disabled)
        self.receiverEdit.setDisabled(disabled)
        self.testBtn.setDisabled(disabled)
        self.verifyBtn.setDisabled(disabled)
        self.applyBtn.setDisabled(disabled)

        self.authorizeBtn.setDisabled(disabled)

    def emailSettingsVerify(self):
        self.clearNotifyMessage()
        self.disabledPage(True)
        self.loadingIcon.setText(self.getTranslateString(i18nId.i18nId().Verifying))
        self.loadingIcon.show()
        self.isVerifying = True
        self.verifyEmailSettingSignal.emit()

    def verfiyEmailResult(self, result):
        self.loadingIcon.hide()
        self.isVerifying = False
        self._refreshSignal.emit(self)
        if result:
            self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Verify_Success))
        else:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Verify_Failure))

    def applyResult(self, result):
        if result:
            self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Apply_Success))
        else:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Apply_Error))

    def collectEmailData(self):
        emailData = EmailNotification()

        # active
        if self.activeB1.isChecked():
            emailData.active = True
        else:
            emailData.active = False

        # serviceProvider
        emailData.serviceProvider = self.serviceDDL.currentIndex()
        # securityConnection
        if self.secB1.isChecked():
            emailData.securityConnection = 0
        elif self.secB2.isChecked():
            emailData.securityConnection = 1
        elif self.secB3.isChecked():
            emailData.securityConnection = 2

        # smtp server
        emailData.smtpServiceAddress = self.smtpAddrEdit.text()

        # security connection
        emailData.servicePort = self.servicePortEdit.text()

        emailData.senderName = self.senderNameEdit.text()
        emailData.senderEmailAddress = self.senderEmailAddress.text()

        if self.authB1.isChecked():
            emailData.needAuth = True
        else:
            emailData.needAuth = False

        emailData.authAccount = self.authAccountEdit.text()
        emailData.authPassword = self.authPasswordEdit.text()
        emailData.receivers = self.receiverEdit.text()

        return emailData

    def decideOauthShowWidget(self, isAuthed, senderName):
        if isAuthed:
            self.isOauthed = True
            self.authedLabel.setText(senderName)
        else:
            self.isOauthed = False

        print("self.serviceDDL.currentIndex: " + str(self.serviceDDL.currentIndex()))
        if self.serviceDDL.currentIndex() == 0:
            if isAuthed:
                self.notAuthFrame.hide()
                self.authedFrame.show()
            else:
                self.authedFrame.hide()
                self.notAuthFrame.show()

    def isVerifyEnable(self, isDisabled):
        self.verifyBtn.setDisabled(isDisabled)
        self.testBtn.setDisabled(isDisabled)

    def fillEmailData(self, emailData):
        # emailData
        try:
            if emailData.active is not None:
                self.activeB1.setChecked(emailData.active)
                self.activeB2.setChecked(not emailData.active)
            if emailData.smtpServiceAddress is not None:
                self.smtpAddrEdit.setText(emailData.smtpServiceAddress)
            if emailData.serviceProvider is not None:
                self.serviceDDL.setCurrentIndex(emailData.serviceProvider)
            if emailData.securityConnection is not None:
                if emailData.securityConnection == 0:
                    self.secB1.setChecked(True)
                    self.secB2.setChecked(False)
                    self.secB3.setChecked(False)
                elif emailData.securityConnection == 1:
                    self.secB1.setChecked(False)
                    self.secB2.setChecked(True)
                    self.secB3.setChecked(False)
                elif emailData.securityConnection == 2:
                    self.secB1.setChecked(False)
                    self.secB2.setChecked(False)
                    self.secB3.setChecked(True)

            if emailData.servicePort is not None:
                self.servicePortEdit.setText(str(emailData.servicePort))

            if emailData.senderName is not None:
                self.senderNameEdit.setText(emailData.senderName)
            if emailData.senderEmailAddress is not None:
                self.senderEmailAddress.setText(emailData.senderEmailAddress)
            if emailData.needAuth is not None:
                self.authB1.setChecked(emailData.needAuth)
                self.authB2.setChecked(not emailData.needAuth)
            if emailData.authAccount is not None:
                self.authAccountEdit.setText(emailData.authAccount)
            if emailData.authPassword is not None:
                self.authPasswordEdit.setText(emailData.authPassword)
            if emailData.receivers is not None:
                self.receiverEdit.setText(emailData.receivers)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def oauthRequest(self):

        # clear apply message
        self.clearNotifyMessage()

        self.authedFrame.hide()
        self.notAuthFrame.show()
        self.oauthCodeEdit.show()
        self.oauthCodeEdit.setPlaceholderText(self.getTranslateString(i18nId.i18nId().Enter_the_authorization_code_here))
        self.verifyBtn.setDisabled(True)
        self.testBtn.setDisabled(True)
        try:
            self._oathRequestSignal.emit(self)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def providerChanged(self, currentIndex):
        self.emailSettingsChange()

        self.applyBtn.setDisabled(False)
        # self.verifyBtn.setDisabled(True)
        # self.testBtn.setDisabled(True)
        # clear apply message
        self.clearNotifyMessage(False)
        self.decideShow(currentIndex)

    def decideShow(self, currentIndex):
        self.activeB1.setDisabled(False)
        self.activeB2.setDisabled(False)
        self.serviceDDL.setDisabled(False)
        if currentIndex == 0:
            # show oauth settings
            if self.isOauthed:
                self.authedFrame.show()
            else:
                self.notAuthFrame.show()

            # hide not oauth settings
            self.smtpServerAddressFrame.hide()
            self.secureConnFrame.hide()
            self.servicePortFrame.hide()
            self.senderAddressFrame.hide()
            self.needAuthFrame.hide()
            self.authAccountFrame.hide()
            self.authPasswordFrame.hide()
            self.senderNameEdit.setDisabled(False)
            self.receiverEdit.setDisabled(False)
            self.authorizeBtn.setDisabled(False)
            self.oauthStep1.setDisabled(False)
            self.oauthCodeEdit.setDisabled(False)
        elif currentIndex == 1:
            self.smtpAddrEdit.setDisabled(False)
            self.secB1.setDisabled(False)
            self.secB2.setDisabled(False)
            self.secB3.setDisabled(False)
            self.servicePortEdit.setDisabled(False)
            self.senderNameEdit.setDisabled(False)
            self.senderEmailAddress.setDisabled(False)
            self.authB1.setDisabled(False)
            self.authB2.setDisabled(False)
            self.authAccountEdit.setDisabled(False)
            self.authPasswordEdit.setDisabled(False)
            self.receiverEdit.setDisabled(False)
            # show not oauth settings
            self.smtpServerAddressFrame.show()
            self.secureConnFrame.show()
            self.servicePortFrame.show()
            self.senderAddressFrame.show()
            self.needAuthFrame.show()
            self.authAccountFrame.show()
            self.authPasswordFrame.show()

            # hide oauth settings
            self.notAuthFrame.hide()
            self.authedFrame.hide()

    def secureConnectCheck(self, button):
        try:
            print(button.text())
            print(CONNECT_TLS)
            if button.text() == CONNECT_TLS:
                self.secConnectTip.setText(DEFAULT_TLS_PORT_MESG)
            elif button.text() == CONNECT_SSL:
                self.secConnectTip.setText(DEFAULT_SSL_PORT_MESG)
            elif button.text() == CONNECT_NONE:
                self.secConnectTip.setText(DEFAULT_NONE_PORT_MESG)
            self.emailSettingsChange()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def emailSettingsChange(self):
        self.applyBtn.setDisabled(False)
        self.verifyBtn.setDisabled(True)
        self.testBtn.setDisabled(True)
        self.errorMsg.setText("")

    def clearNotifyMessage(self, isTestDisable=True, isVerifyDisabled=True):
        self.errorMsg.setText("")

    def updatePageWithSocket(self, updateData):
        # self.alarmEnableRadioBtn.setEnabled(True)
        # self.alarmDisableRadioBtn.setEnabled(True)
        # print("alarm:" + str(updateData.upsAlarmEnable))
        if updateData.upsAlarmEnable == ViewData.UpsAlarmEnum.Enabled.value:
            self.alarmEnableRadioBtn.setChecked(True)
        else:
            self.alarmDisableRadioBtn.setChecked(True)

    def restoreSettings(self, configData):
        if configData.softwareSoundEnable:
            self.softCheckBox.setChecked(True)
        else:
            self.softCheckBox.setChecked(False)

    def disableConfigure(self):
        self.alarmEnableRadioBtn.setDisabled(True)
        self.alarmDisableRadioBtn.setDisabled(True)

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Notification))
        self.softTitleLable.setText(self.getTranslateString(i18nId.i18nId().Software_Sounds))
        self.softMsgLabel.setText(self.getTranslateString(
            i18nId.i18nId().application_short_name_generates_audible_sounds_to_notify_you_of_power_events))
        self.softCheckBox.setText(
            self.getTranslateString(i18nId.i18nId().Enable_application_short_name_notification_sounds))
        self.upsAlarmTitleLabel.setText(self.getTranslateString(i18nId.i18nId().UPS_Alarms))
        self.upsAlarmMsgLabel.setText(
            self.getTranslateString(i18nId.i18nId().The_UPS_generates_audible_alarms_during_power_events))
        self.alarmEnableRadioBtn.setText(self.getTranslateString(i18nId.i18nId().Enable_alarms_at_all_times))
        self.alarmDisableRadioBtn.setText(self.getTranslateString(i18nId.i18nId().Disable_alarms_at_all_times))

        # mail
        self.label_5.setText(self.getTranslateString(i18nId.i18nId().Email))
        self.mailLabel1.setText(self.getTranslateString(i18nId.i18nId().Activate))
        self.activeB1.setText(self.getTranslateString(i18nId.i18nId().Yes))
        self.activeB2.setText(self.getTranslateString(i18nId.i18nId().No))
        self.mailLabel2.setText(self.getTranslateString(i18nId.i18nId().Service_Provider))
        # self.serviceDDL.addItem("gmail")

        # self.serviceDDL.addItem("Other")
        self.serviceDDL.setItemText(1, self.getTranslateString(i18nId.i18nId().other))
        self.mailLabelOAuth.setText(self.getTranslateString(i18nId.i18nId().Account))
        self.oauthStep1.setText(self.getTranslateString(i18nId.i18nId().Request))
        self.authorizeBtn.setText(self.getTranslateString(i18nId.i18nId().Change))
        self.mailLabel3.setText(self.getTranslateString(i18nId.i18nId().SMTP_server_address))
        self.mailLabel4.setText(self.getTranslateString(i18nId.i18nId().Secure_connection))
        self.mailLabel5.setText(self.getTranslateString(i18nId.i18nId().Service_port))
        self.mailLabel6.setText(self.getTranslateString(i18nId.i18nId().Sender_name))
        self.mailLabel7.setText(self.getTranslateString(i18nId.i18nId().Sender_Email_address))
        self.mailLabel8.setText(self.getTranslateString(i18nId.i18nId().Authentication))
        self.mailLabel9.setText(self.getTranslateString(i18nId.i18nId().Account))
        self.authB1.setText(self.getTranslateString(i18nId.i18nId().Yes))
        self.authB2.setText(self.getTranslateString(i18nId.i18nId().No))
        self.mailLabel10.setText(self.getTranslateString(i18nId.i18nId().Password))
        self.mailLabel11.setText(self.getTranslateString(i18nId.i18nId().Receiver_Email_address))
        self.testBtn.setText(self.getTranslateString(i18nId.i18nId().Test))
        self.applyBtn.setText(self.getTranslateString(i18nId.i18nId().Apply))
        self.verifyBtn.setText(self.getTranslateString(i18nId.i18nId().Verify))


    def updatePageByStatus(self, daemonStatus):
        if daemonStatus and not daemonStatus.isDaemonStarted:
            self.softCheckBox.setDisabled(True)
            self.disabledPage(True)
            self.oauthStep1.setDisabled(True)
            self.alarmEnableRadioBtn.setDisabled(True)
            self.alarmDisableRadioBtn.setDisabled(True)
            self.daemonStatusFlag = False
            self.oauthCodeEdit.setDisabled(True)
        elif daemonStatus and daemonStatus.isDaemonStarted:
            self.softCheckBox.setDisabled(False)
            self.daemonStatusFlag = True
            pass

        # check UPS alarm set
        if daemonStatus and daemonStatus.deviceId == -1:
            # self.disabledPage(False)
            # self.oauthStep1.setDisabled(False)
            self.alarmEnableRadioBtn.setDisabled(True)
            self.alarmDisableRadioBtn.setDisabled(True)
            # self.daemonStatusFlag = False
            # self.oauthCodeEdit.setDisabled(False)

        elif daemonStatus and daemonStatus.deviceId != -1:
            # self.disabledPage(False)
            # self.oauthStep1.setDisabled(False)
            self.alarmEnableRadioBtn.setDisabled(False)
            self.alarmDisableRadioBtn.setDisabled(False)
            # self.daemonStatusFlag = True
            # self.oauthCodeEdit.setDisabled(False)

    class DisplayData:
        def __init__(self):
            self.upsAlarmEnable = 0


class QTextMovieLabel(QLabel):
    def __init__(self, text, fileName):
        QLabel.__init__(self)
        self._text = text
        m = QMovie(fileName)
        m.start()
        self.setMovie(m)

    def setMovie(self, movie):
        QLabel.setMovie(self, movie)
        s = movie.currentImage().size()
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
