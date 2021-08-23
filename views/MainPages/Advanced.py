import os
import traceback
import webbrowser

from PyQt5 import QtCore, QtWidgets
from functools import partial

import sys
from PyQt5.QtCore import pyqtSignal, QRegExp, QEvent, Qt, QTimer, QSize
from PyQt5.QtGui import QRegExpValidator, QPixmap, QMovie
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QComboBox, QPushButton, QCheckBox, QLineEdit, QDialog, QGridLayout, QScrollArea, QFrame)

from Utility import DataCryptor
from Utility.HelpOpener import HelpOpener
from i18n import i18nId, appLocaleData
from System import settings, systemFunction, systemDefine
from model_Json.WebAppData import CloudLoginData
from model_Json.tables.Account import Account
from views.Custom import ViewData
from views.Custom.ViewData import ShutdownTypeEnum, InputVoltageSensitivity
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox

ERROR_MSG_STYLE = "color: #db232b; margin-top: 10px;"
SUCCESS_MSG_STYLE = "color: #1b44e8; margin-top: 10px;"

class Advanced(TemplatePage.TemplatePage):
    _setShutdownTypeSignal = pyqtSignal(object)
    _setSensitivitySignal = pyqtSignal(object)
    _viewSetMobileSolutionSignal = pyqtSignal(object)
    _viewSetMobileLoginSignal = pyqtSignal(object)
    _viewUpdateUPSNameSignal = pyqtSignal(object)
    _get_cloud_data_signal = pyqtSignal(object)
    _cloud_verify_signal = pyqtSignal(object)

    def __init__(self):
        super(Advanced, self).__init__()
        self.setAccessibleName("advancedpage")
        self.configGroup = None
        self.sensitivityLabel = None
        self.sensitivityMsgLabel = None
        self.sensitivityMsg2Label = None
        self.sensitivityTailLabel = None
        self.funcEnableFlag = False
        self.UPSNameEditFlag = True
        self.initFlag = True

        self.init_ui()

    def init_ui(self):

        # <editor-fold desc="Main data fields">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("advanceQGroupBox")
        self.configGroup.setAccessibleName("advancedpagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("advancedpagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("advanced.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')
        # mainTitleLayout.addStretch(1)
        mainTitleLayout.setSpacing(0)
        mainTitleLayout.setContentsMargins(0, 0, 0, 0)

        self.sensitivityLabel = label_1 = QLabel()
        label_1.setProperty('class', 'label-LeftCls')
        self.sensitivityMsgLabel = label_2 = QLabel()
        # 2019/02/23 Kenneth
        self.sensitivityMsgLabel.setWordWrap(True)
        self.sensitivityMsg2Label = label_3 = QLabel()
        self.sensitivityDDL = sensitivityDDL = ComboBox()
        self.sensitivityDDL.setAccessibleName("advancedpagesensitivityselect")
        sensitivityDDL.setProperty('class', 'advancedComboCls')
        # 2019/02/23 Kenneth Setting for dropdown list line-height
        self.sensitivityDDL.setView(QtWidgets.QListView())
        self.sensitivityDDL.activated.connect(lambda: self.setSensitivity(self.sensitivityDDL))
        self.sensitivityTailLabel = label_4 = QLabel()
        self.line1 = ViewData.QHLine()
        self.sensitivityFuncDisplay()

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(label_3)
        hlayout1.addWidget(sensitivityDDL)
        hlayout1.addWidget(label_4)
        hlayout1.addStretch(1)

        self.label_5 = QLabel()
        self.label_5.setProperty('class', 'label-LeftCls2')
        self.label_6 = QLabel()
        self.label_7 = QLabel("Shutdown type")
        self.label_7.setProperty('class', 'label-LeftCls-type')
        self.shutdownTypeDDL = ComboBox()
        self.shutdownTypeDDL.setAccessibleName("advancedpageshutdowntypeselect")
        for item in ShutdownTypeEnum:
            self.shutdownTypeDDL.addItem(str(item.name), str(item.value))

        self.shutdownTypeDDL.setProperty('class', 'advancedComboCls-type')
        self.shutdownTypeDDL.activated.connect(lambda: self.whichbtn(self.shutdownTypeDDL))
        # 2019/02/23 Kenneth Setting for dropdown list line-height
        self.shutdownTypeDDL.setView(QtWidgets.QListView())
        self.shutdownTypeDDL.setFixedWidth(170)
        self.sensitivityDDL.setEnabled(False)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.label_7)
        hlayout2.addWidget(self.shutdownTypeDDL)
        hlayout2.addStretch(1)

        # PowerPanel Cloud Solution
        cloud_hlayout = QHBoxLayout()
        cloud_solution_vlayout = QVBoxLayout()

        # Title
        self.cloud_title_label = QLabel()
        self.cloud_title_label.setProperty('class', 'cloud_title_label')
        self.cloud_title_label.setText('PowerPanel Cloud Solution')
        cloud_solution_vlayout.addWidget(self.cloud_title_label)

        # Connect
        connect_hlayout = QHBoxLayout()
        self.connect_label = QLabel()
        self.connect_label.setProperty('class', 'cloud_label')
        self.connect_label.setText('Connect')
        self.connect_label.setFixedWidth(170)

        self.connect_check_box = QCheckBox()
        self.connect_check_box.setProperty('class', 'cloud_connect_check_box')
        self.connect_check_box.setText('')
        self.connect_check_box.stateChanged.connect(self.connect_checkbox_statechange_event)

        connect_hlayout.addWidget(self.connect_label)
        connect_hlayout.addWidget(self.connect_check_box)
        cloud_solution_vlayout.addLayout(connect_hlayout)

        # Account
        account_hlayout = QHBoxLayout()
        self.account_label = QLabel()
        self.account_label.setProperty('class', 'cloud_label')
        self.account_label.setText('Account')
        self.account_label.setFixedWidth(170)

        self.account_line_edit = QLineEdit('')
        self.account_line_edit.setProperty('class', 'cloud_account_line_edit')
        self.account_line_edit.setText('')
        self.account_line_edit.textChanged.connect(self.textChanged_event)

        account_hlayout.addWidget(self.account_label)
        account_hlayout.addWidget(self.account_line_edit)
        cloud_solution_vlayout.addLayout(account_hlayout)

        # Password
        password_hlayout = QHBoxLayout()
        self.password_label = QLabel()
        self.password_label.setProperty('class', 'cloud_label')
        self.password_label.setText('Password')
        self.password_label.setFixedWidth(170)

        self.password_line_edit = QLineEdit('')
        self.password_line_edit.setProperty('class', 'cloud_account_line_edit')
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.password_line_edit.setText('')
        self.password_line_edit.textChanged.connect(self.textChanged_event)

        password_hlayout.addWidget(self.password_label)
        password_hlayout.addWidget(self.password_line_edit)
        cloud_solution_vlayout.addLayout(password_hlayout)

        # UPS Name
        ups_name_hlayout = QHBoxLayout()
        self.ups_name_label = QLabel()
        self.ups_name_label.setProperty('class', 'cloud_label')
        self.ups_name_label.setText('UPS Name')
        self.ups_name_label.setFixedWidth(170)

        self.ups_name_line_edit = QLineEdit('')
        self.ups_name_line_edit.setProperty('class', 'cloud_account_line_edit')
        self.ups_name_line_edit.setText('')
        self.ups_name_line_edit.textChanged.connect(self.textChanged_event)

        ups_name_hlayout.addWidget(self.ups_name_label)
        ups_name_hlayout.addWidget(self.ups_name_line_edit)
        cloud_solution_vlayout.addLayout(ups_name_hlayout)

        # Terms and Policy
        terms_and_policy_hlayout = QHBoxLayout()
        self.urlLink1 = ''
        self.urlLink2 = ''
        self.changeUrlLinkBylocale(appLocaleData.appLocaleRecorder().appLocale)
        labelStr = self.getTranslateString(i18nId.i18nId().I_agree_to_the) \
            .replace("xxxx0", self.urlLink2)\
            .replace("xxxx1", self.urlLink1)

        self.terms_and_policy_check_box = QCheckBox()
        self.terms_and_policy_check_box.setProperty('class', 'cloud_terms_and_policy_check_box')
        self.terms_and_policy_check_box.stateChanged.connect(self.terms_and_policy_checkbox_statechanged_event)
        self.terms_and_policy_check_box.setContentsMargins(0, 0, 0, 0)

        self.terms_and_policy_label = QLabel()
        self.terms_and_policy_label.setProperty('class', 'cloud_terms_and_policy_label')
        self.terms_and_policy_label.setOpenExternalLinks(True)
        self.terms_and_policy_label.setText(labelStr)
        self.terms_and_policy_label.setWordWrap(True)
        self.terms_and_policy_label.setContentsMargins(0, 0, 0, 0)

        terms_and_policy_hlayout.setSpacing(0)
        terms_and_policy_hlayout.setContentsMargins(0, 0, 0, 0)
        terms_and_policy_hlayout.addWidget(self.terms_and_policy_check_box)
        terms_and_policy_hlayout.addWidget(self.terms_and_policy_label)
        cloud_solution_vlayout.addLayout(terms_and_policy_hlayout)

        # Result Message
        self.result_message_label = QLabel("Applied Successfully")
        self.result_message_label.setStyleSheet(SUCCESS_MSG_STYLE)
        self.result_message_label.hide()
        self.result_message_label.setProperty('class', 'result_message')
        self.result_message_label.setContentsMargins(5, 0, 0, 0)
        self.result_message_label.setStyleSheet(SUCCESS_MSG_STYLE)
        cloud_solution_vlayout.addWidget(self.result_message_label)

        # Button
        button_hlayout = QHBoxLayout()

        self.cancel_button = QPushButton()
        self.cancel_button.setProperty('class', 'cloud_cancel_button')
        self.cancel_button.setText('Cancel')
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_button_click_event)

        self.apply_button = QPushButton()
        self.apply_button.setProperty('class', 'cloud_apply_button')
        self.apply_button.setText('Apply')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_button_click_event)

        self.verify_button = QPushButton()
        self.verify_button.setProperty('class', 'cloud_verify_button')
        self.verify_button.setText('Verify')
        self.verify_button.setEnabled(False)
        self.verify_button.clicked.connect(self.verify_button_click_event)

        button_hlayout.addWidget(self.cancel_button)
        button_hlayout.addWidget(self.apply_button)
        button_hlayout.addWidget(self.verify_button)
        cloud_solution_vlayout.addLayout(button_hlayout)

        # Active to Get Free Trial
        get_free_trial_vlayout = QVBoxLayout()

        # Title
        self.free_trial_title_label = QLabel()
        self.free_trial_title_label.setProperty('class', 'cloud_title_label_active')
        self.free_trial_title_label.setText('Active to Get Free Trial')
        get_free_trial_vlayout.addWidget(self.free_trial_title_label)
        self.free_trial_title_label.setWordWrap(True)

        # PowerPanel Cloud Link
        cloud_link_hlayout = QHBoxLayout()
        link_label = "<a style='color:#666666' class='link' href=\"https://powerpanel.cyberpower.com\">PowerPanel Cloud</a>"
        self.cloud_link_label = QLabel(link_label)
        self.cloud_link_label.setProperty('class', 'cloud_link_label')
        self.cloud_link_label.setOpenExternalLinks(True)
    

        self.cloud_link_image_content = QLabel()
        self.cloud_link_image = QPixmap(os.path.join(settings.IMAGE_PATH, "icon_link.png"))
        self.cloud_link_image_content.setPixmap(self.cloud_link_image)

        cloud_link_hlayout.addWidget(self.cloud_link_label)
        cloud_link_hlayout.addWidget(self.cloud_link_image_content)
        cloud_link_hlayout.setSpacing(0)
        get_free_trial_vlayout.addLayout(cloud_link_hlayout)

        # PowerPanel App Title
        self.app_title_label = QLabel()
        self.app_title_label.setProperty('class', 'cloud_app_title_label')
        self.app_title_label.setText('PowerPanel App')

        get_free_trial_vlayout.addWidget(self.app_title_label)

        # QRCode Image
        self.app_qrcode_content = QLabel()
        self.app_qrcode_image = QPixmap(os.path.join(settings.IMAGE_PATH, 'PPC_download.png'))
        self.app_qrcode_content.setPixmap(self.app_qrcode_image)
        self.app_qrcode_content.setContentsMargins(0, 0, 0, 0)
        get_free_trial_vlayout.addWidget(self.app_qrcode_content)
        get_free_trial_vlayout.addStretch(1)
        get_free_trial_vlayout.setContentsMargins(30, 0, 0, 0)

        cloud_hlayout.addLayout(cloud_solution_vlayout)
        cloud_hlayout.addLayout(get_free_trial_vlayout)
        cloud_hlayout.addStretch(1)

        ############

        vlayout1 = QVBoxLayout()
        vlayout1.addWidget(label_1)
        vlayout1.addWidget(label_2)
        vlayout1.addLayout(hlayout1)
        vlayout1.addWidget(self.line1)
        vlayout1.addWidget(self.label_5)
        vlayout1.addWidget(self.label_6)
        vlayout1.addLayout(hlayout2)
        vlayout1.addWidget(ViewData.QHLine())

        # PowerPanel Cloud layout
        vlayout1.addLayout(cloud_hlayout)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(vlayout1)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 20)
        # serverLayoutAll.setSpacing(0)
        configGroup.setLayout(serverLayoutAll)

        # </editor-fold>

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

        self.renderText()
        self.setLayout(mainLayout)

    def sensitivityFuncDisplay(self):
        self.sensitivityLabel.setVisible(self.funcEnableFlag)
        self.sensitivityMsgLabel.setVisible(self.funcEnableFlag)
        self.sensitivityMsg2Label.setVisible(self.funcEnableFlag)
        self.sensitivityDDL.setVisible(self.funcEnableFlag)
        self.sensitivityTailLabel.setVisible(self.funcEnableFlag)
        self.line1.setVisible(self.funcEnableFlag)

    @property
    def setShutdownTypeSignal(self):
        return self._setShutdownTypeSignal

    @setShutdownTypeSignal.setter
    def setShutdownTypeSignal(self, value):
        self._setShutdownTypeSignal = value

    @property
    def setSensitivitySignal(self):
        return self._setSensitivitySignal

    @setSensitivitySignal.setter
    def setSensitivitySignal(self, value):
        self._setSensitivitySignal = value

    @property
    def viewSetMobileSolutionSignal(self):
        return self._viewSetMobileSolutionSignal

    @viewSetMobileSolutionSignal.setter
    def viewSetMobileSolutionSignal(self, value):
        self._viewSetMobileSolutionSignal = value

    @property
    def viewSetMobileLoginSignal(self):
        return self._viewSetMobileLoginSignal

    @viewSetMobileLoginSignal.setter
    def viewSetMobileLoginSignal(self, value):
        self._viewSetMobileLoginSignal = value

    @property
    def viewUpdateUPSNameSignal(self):
        return self._viewUpdateUPSNameSignal

    @viewUpdateUPSNameSignal.setter
    def viewUpdateUPSNameSignal(self, value):
        self._viewUpdateUPSNameSignal = value

    @property
    def get_cloud_data_signal(self):
        return self._get_cloud_data_signal

    @get_cloud_data_signal.setter
    def get_cloud_data_signal(self, value):
        self._get_cloud_data_signal = value

    @property
    def cloud_verify_signal(self):
        return self._cloud_verify_signal

    @cloud_verify_signal.setter
    def cloud_verify_signal(self, value):
        self._cloud_verify_signal = value

    def whichbtn(self, b):
        setConfigData = int(self.shutdownTypeDDL.currentData())
        self._setShutdownTypeSignal.emit(setConfigData)

    def restoreConfigSetting(self, config):
        value = int(config.shutDownType)
        index = self.shutdownTypeDDL.findData(value) # Returns the index of the item containing the given data for the given role; otherwise returns -1.
        if index >= 0:
            self.shutdownTypeDDL.setCurrentIndex(index)

    def updatePage(self, updateData):
        try:
            value = int(updateData.sensitivity)
            ddlText = InputVoltageSensitivity(value).name
            index1 = self.sensitivityDDL.findText(ddlText, QtCore.Qt.MatchFixedString)
            if index1 >= 0:
                self.sensitivityDDL.setCurrentIndex(index1)
        except Exception:
            print("sensitive invalid")

    def updatePageByStatus(self, daemonStatus):
        disabledFlag = True
        self.sensitivityDDL.setDisabled(disabledFlag)
        self.shutdownTypeDDL.setDisabled(disabledFlag)

    def updatePageWithSocket(self, updateData):
        try:
            value = int(updateData.sensitivity)
            self.funcEnableFlag = any(value == item.value for item in InputVoltageSensitivity)
            self.sensitivityFuncDisplay()

            if self.funcEnableFlag:
                if self.sensitivityDDL.count() == 0:
                    for item in InputVoltageSensitivity:
                        self.sensitivityDDL.addItem(str(item.name), str(item.value))

                ddlText = InputVoltageSensitivity(value).name
                index1 = self.sensitivityDDL.findText(ddlText, QtCore.Qt.MatchFixedString)
                if index1 >= 0:
                    self.sensitivityDDL.setCurrentIndex(index1)
            else:
                self.sensitivityDDL.clear()
                self.sensitivityDDL.setEnabled(False)
                pass

        except Exception:
            # value invaliad
            self.sensitivityDDL.clear()
            self.sensitivityDDL.setEnabled(False)
            print("sensitive invalid")

    def setSensitivity(self, b):
        param = int(b.currentData())
        self._setSensitivitySignal.emit(param)

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Advanced))
        self.sensitivityLabel.setText(self.getTranslateString(i18nId.i18nId().Input_Voltage_Sensitivity))
        self.sensitivityMsgLabel.setText(self.getTranslateString(
            i18nId.i18nId().You_can_select_an_adequate_sensitivity_according_to_the_equipment_and_the_power))

        wordingArr1 = self.getTranslateString(i18nId.i18nId().Controls_the_power_quality_according_to_xxxx_sensitivity).split("xxxx")
        self.sensitivityMsg2Label.setText(wordingArr1[0])
        self.sensitivityTailLabel.setText(wordingArr1[1])

        self.label_5.setText(self.getTranslateString(i18nId.i18nId().Shutdown_Type))
        self.label_6.setText(self.getTranslateString(i18nId.i18nId().You_can_specify_the_manner_in_which_the_computer_is_shutdown))
        self.label_7.setText(self.getTranslateString(i18nId.i18nId().Shutdown_Type))

        self.sensitivityDDL.setItemText(0, self.getTranslateString(i18nId.i18nId().Low))
        self.sensitivityDDL.setItemText(1, self.getTranslateString(i18nId.i18nId().Medium))
        self.sensitivityDDL.setItemText(2, self.getTranslateString(i18nId.i18nId().High))
        self.shutdownTypeDDL.setItemText(0, self.getTranslateString(i18nId.i18nId().Shutdown))
        self.shutdownTypeDDL.setItemText(1, self.getTranslateString(i18nId.i18nId().Hibernation))

        # PowerPanel Cloud
        self.cloud_title_label.setText(self.getTranslateString(i18nId.i18nId().PowerPanel_Cloud_Solution))
        self.connect_label.setText(self.getTranslateString(i18nId.i18nId().Connect))
        self.account_label.setText(self.getTranslateString(i18nId.i18nId().Account))
        self.password_label.setText(self.getTranslateString(i18nId.i18nId().Password))
        self.ups_name_label.setText(self.getTranslateString(i18nId.i18nId().UPS_Name))
        self.cancel_button.setText(self.getTranslateString(i18nId.i18nId().Cancel))
        self.apply_button.setText(self.getTranslateString(i18nId.i18nId().Apply))
        self.verify_button.setText(self.getTranslateString(i18nId.i18nId().Verify))

        self.changeUrlLinkBylocale(appLocaleData.appLocaleRecorder().appLocale)
        labelStr = self.getTranslateString(i18nId.i18nId().I_agree_to_the) \
            .replace("xxxx0", self.urlLink2) \
            .replace("xxxx1", self.urlLink1)
        self.terms_and_policy_label.setText(labelStr)

        # Get Free Trial
        self.free_trial_title_label.setText(self.getTranslateString(i18nId.i18nId().Activate_to_Get_Free_Trial))
        link_label = "<a style='color:#666666' class='link' href=\"https://powerpanel.cyberpower.com\">" + \
                     self.getTranslateString(i18nId.i18nId().PowerPanel_Cloud) + "</a>"
        self.cloud_link_label.setText(link_label)
        self.app_title_label.setText(self.getTranslateString(i18nId.i18nId().PowerPanel_App))

    def mobileAppLoginDisplay(self, response):
        try:
            if response.Flag:
                self.result_message_label.setText(self.getTranslateString(i18nId.i18nId().Cloud_Apply_Success))
                self.result_message_label.setStyleSheet(SUCCESS_MSG_STYLE)
                # 開啟Verify按鈕的功能
                self.verify_button.setEnabled(True)
                webbrowser.open(systemDefine.POWERPANEL_CLOUD_WEBSIDE)
            else:
                if response.Message == i18nId.i18nId().Cloud_Error_Occurred:
                    self.result_message_label.setText(self.getTranslateString(i18nId.i18nId().Cloud_Error_Occurred))
                elif response.Message == i18nId.i18nId().Cloud_Incorrect_Account_or_Password:
                    self.result_message_label.setText(self.getTranslateString(i18nId.i18nId().Cloud_Incorrect_Account_or_Password))
                self.result_message_label.setStyleSheet(ERROR_MSG_STYLE)
            self.result_message_label.show()

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cloud_data_display(self, cloud_data):
        try:
            if cloud_data.connect:
                self.connect_check_box.setChecked(True)

            if cloud_data.account:
                self.account_line_edit.setText(cloud_data.account)

            if cloud_data.password:
                cryptor = DataCryptor.Cryptor()
                dec_pass = cryptor.decToString(cloud_data.password)
                self.password_line_edit.setText(dec_pass)

            if cloud_data.ups_name:
                self.ups_name_line_edit.setText(cloud_data.ups_name)

            if cloud_data.agree_policy:
                self.terms_and_policy_check_box.setChecked(True)
                self.apply_button.setEnabled(False)
                self.cancel_button.setEnabled(False)
            else:
                self.terms_and_policy_check_box.setChecked(False)

            if cloud_data.verifiable:
                self.verify_button.setEnabled(True)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def cloud_verify_result_display(self, response):
        try:
            if response.Flag:
                self.result_message_label.setText(self.getTranslateString(i18nId.i18nId().Cloud_Verify_Success))
            else:
                if response.Message == i18nId.i18nId().Cloud_Incorrect_Account_or_Password:
                    self.result_message_label.setText(
                        self.getTranslateString(i18nId.i18nId().Cloud_Incorrect_Account_or_Password))
                else:
                    self.result_message_label.setText(self.getTranslateString(i18nId.i18nId().Cloud_Error_Occurred))
            self.result_message_label.show()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def connect_checkbox_statechange_event(self, state):
        self.cancel_button.setEnabled(True)
        if self.terms_and_policy_check_box.checkState().real is ViewData.CheckBoxState.checked.value:
            self.apply_button.setEnabled(True)

    def terms_and_policy_checkbox_statechanged_event(self, state):
        self.cancel_button.setEnabled(True)
        if state == ViewData.CheckBoxState.unchecked.value:
            self.apply_button.setEnabled(False)
        elif state == ViewData.CheckBoxState.checked.value:
            self.apply_button.setEnabled(True)

    def textChanged_event(self, text):
        self.cancel_button.setEnabled(True)
        if self.terms_and_policy_check_box.checkState().real is ViewData.CheckBoxState.checked.value:
            self.apply_button.setEnabled(True)

    def apply_button_click_event(self):
        cloud_data = CloudLoginData()

        cloud_data.account = self.account_line_edit.text()
        cloud_data.password = self.password_line_edit.text()
        cloud_data.ups_name = self.ups_name_line_edit.text()

        if self.connect_check_box.checkState().real is ViewData.CheckBoxState.checked.value:
            cloud_data.connect = True
        else:
            cloud_data.connect = False

        if self.terms_and_policy_check_box.checkState().real is ViewData.CheckBoxState.checked.value:
            cloud_data.agree_policy = True
        else:
            cloud_data.agree_policy = False

        self.viewSetMobileLoginSignal.emit(cloud_data)

        # 關閉按鈕功能
        self.cancel_button.setEnabled(False)
        self.apply_button.setEnabled(False)

    def verify_button_click_event(self):
        self.cloud_verify_signal.emit(None)

    def cancel_button_click_event(self):
        self.get_cloud_data_signal.emit(None)
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def changeUrlLinkBylocale(self, localeStr):

        urlLink1 = "<a style='color:#000000;' class='link' href=\""
        urlLink2 = "<a style='color:#000000;' class='link' href=\""

        if localeStr == appLocaleData.appLocaleData().en_US:
            urlLink1 += appLocaleData.appLocaleData().en_US_privacy_url
            urlLink2 += appLocaleData.appLocaleData().en_US_terms_url

        elif localeStr == appLocaleData.appLocaleData().de_DE:
            urlLink1 += appLocaleData.appLocaleData().de_DE_privacy_url
            urlLink2 += appLocaleData.appLocaleData().de_DE_terms_url

        elif localeStr == appLocaleData.appLocaleData().ja_JP:
            urlLink1 += appLocaleData.appLocaleData().ja_JP_privacy_url
            urlLink2 += appLocaleData.appLocaleData().ja_JP_terms_url

        elif localeStr == appLocaleData.appLocaleData().cs_CZ:
            urlLink1 += appLocaleData.appLocaleData().cs_CZ_privacy_url
            urlLink2 += appLocaleData.appLocaleData().cs_CZ_terms_url

        elif localeStr == appLocaleData.appLocaleData().pl:
            urlLink1 += appLocaleData.appLocaleData().pl_privacy_url
            urlLink2 += appLocaleData.appLocaleData().pl_terms_url

        elif localeStr == appLocaleData.appLocaleData().es_ES:
            urlLink1 += appLocaleData.appLocaleData().es_ES_privacy_url
            urlLink2 += appLocaleData.appLocaleData().es_ES_terms_url

        else:
            urlLink1 += appLocaleData.appLocaleData().en_US_privacy_url
            urlLink2 += appLocaleData.appLocaleData().en_US_terms_url

        urlLink1 += "\">" + self.getTranslateString(
            i18nId.i18nId().Privacy_Policy) + "</a>"
        urlLink2 += "\">" + self.getTranslateString(
            i18nId.i18nId().Terms_Conditions) + "</a>"

        self.urlLink1 = urlLink1
        self.urlLink2 = urlLink2

    class DisplayData:

        def __init__(self):
            self.sensitivity = -1
