import datetime
import os
import platform
import sys
import traceback
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QDialog, QCheckBox, QFrame,
                             QScrollArea)

from System import systemDefine, settings
from i18n import i18nId
from views.Custom import ViewData
from views.MainPages import TemplatePage
from i18n import appLocaleData

PPP_DOWNLOAD_FAILED = "downloading_failed"
PPP_UPDATE_SUCCESS = "updated_success"
PPP_UPDATE_FAILED = "updating_failed"
PPP_RESTORE_SUCCESS = "restored_success"
PPP_RESTORE_FAILED = "restoring_failed"

class About(TemplatePage.TemplatePage, systemDefine.Singleton):
    _check_update_signal = pyqtSignal(object)
    _run_update_signal = pyqtSignal(object)
    _run_restore_signal = pyqtSignal(object)

    def __init__(self):
        super(About, self).__init__()
        self.setAccessibleName("aboutpage")
        self.configGroup = None
        self.versionLabel = None
        self.hardwareInfoLabel = None
        self.modelNameLabel = None
        self.serial_number_label = None
        self.firmVersionLabel = None
        self.powerRatingLabel = None
        self.webInfoLabel = None
        self.websiteLabel = None
        self.productsLabel = None
        self.contactLabel = None
        self.youtubeLabel = None
        self.check_update_btn = None
        self.update_now_btn = None
        self.update_now_label = None
        self.update_now_group = None
        self.update_status_data = None
        self.update_processing_dialog = None
        self.restore_processing_dialog = None
        self.displayData = self.DisplayData()
        self.init_ui()

    def init_ui(self):
        # <editor-fold desc="About UI">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("aboutQGroupBox")
        self.configGroup.setAccessibleName("aboutpagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel(systemDefine.pppName)
        self.mainTitle.setAccessibleName("aboutmaintitle")
        mainTitle.setProperty('class', 'serverLabel_title')

        # qMark = QPushButton("")
        # qMark.setProperty('class', 'qMark')
        # qMark.clicked.connect(lambda: systemFunction.qMarkClicked())

        mainTitleLayout.addWidget(mainTitle)
        # mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        vlayout1 = QVBoxLayout()
        hlayout1_1 = QHBoxLayout()

        self.versionLabel = label_1 = CustumVersionLable("Version " + systemDefine.pppeVersion)
        self.versionLabel.setAccessibleName("aboutversion")
        label_1.setProperty('class', 'label-LeftCls-version')
        hlayout1_1.addWidget(label_1)
        vlayout1.addStretch(1)


        self.check_update_btn = QPushButton("Check for Updates")
        self.check_update_btn.setAccessibleName("check_update")
        self.check_update_btn.setDefault(True)
        self.check_update_btn.clicked.connect(self.check_update)
        self.check_update_btn.setProperty('class', 'btn_check_update')
        hlayout1_1.addWidget(self.check_update_btn)
        vlayout1.addLayout(hlayout1_1)

        vlayout1_2 = QVBoxLayout()
        self.update_now_label = QLabel()
        self.update_now_label.setText("A new version of PowerPanel 2.2.6 is now available")
        self.update_now_label.setAccessibleName("update_now_label")
        self.update_now_label.setProperty('class', 'update_now_label')
        vlayout1_2.addWidget(self.update_now_label)

        self.update_now_btn = QPushButton("Update Now")
        self.update_now_btn.setAccessibleName("update_now")
        self.update_now_btn.setDefault(True)
        self.update_now_btn.setProperty('class', 'btn_update_now')
        self.update_now_btn.clicked.connect(self.run_software_update)
        vlayout1_2.addWidget(self.update_now_btn)

        self.update_now_group = QFrame()
        self.update_now_group.setProperty('class', 'update_now_box')
        self.update_now_group.setLayout(vlayout1_2)
        self.update_now_group.hide()

        vlayout1.addWidget(self.update_now_group)
        vlayout1.addStretch(1)

        #  ----------------------separator----------------------

        vlayout2 = QVBoxLayout()
        self.hardwareInfoLabel = label_2 = QLabel("Hardware Information")
        self.hardwareInfoLabel.setAccessibleName("abouthardwareinformation")
        label_2.setProperty('class', 'label-LeftCls')
        vlayout2.addStretch(1)

        hlayout2_1 = QHBoxLayout()
        self.modelNameLabel = QLabel("Model Name")
        self.modelNameLabel.setAccessibleName("aboutmodelname")
        self.modelNameLabel.setProperty('class', '')
        self.modelNameValue = QLabel(self.getTranslateString(i18nId.i18nId().Unknown))
        hlayout2_1.addWidget(self.modelNameLabel)
        hlayout2_1.addWidget(self.modelNameValue)

        hlayout2_2 = QHBoxLayout()
        self.serial_number_label = QLabel("Serial Number")
        self.serial_number_label.setAccessibleName("aboutserialnumber")
        self.serial_number_label.setProperty('class', '')
        self.serial_number_value = QLabel(self.getTranslateString(i18nId.i18nId().Unknown))
        hlayout2_2.addWidget(self.serial_number_label)
        hlayout2_2.addWidget(self.serial_number_value)

        hlayout2_3 = QHBoxLayout()
        self.firmVersionLabel = QLabel("Firmware Version")
        self.firmVersionLabel.setAccessibleName("aboutfirmwareversion")
        self.firmVersionLabel.setProperty('class', '')
        self.firmVersionValue = QLabel(self.getTranslateString(i18nId.i18nId().Unknown))
        hlayout2_3.addWidget(self.firmVersionLabel)
        hlayout2_3.addWidget(self.firmVersionValue)

        hlayout2_4 = QHBoxLayout()
        self.powerRatingLabel = QLabel("Power Rating")
        self.powerRatingLabel.setAccessibleName("aboutpowerrating")
        self.powerRatingLabel.setProperty('class', '')
        self.powerRatingValue = QLabel(self.getTranslateString(i18nId.i18nId().Unknown))
        hlayout2_4.addWidget(self.powerRatingLabel)
        hlayout2_4.addWidget(self.powerRatingValue)

        vlayout2.addWidget(label_2)
        vlayout2.addLayout(hlayout2_1)
        vlayout2.addLayout(hlayout2_2)
        vlayout2.addLayout(hlayout2_3)
        vlayout2.addLayout(hlayout2_4)

        #  ----------------------separator----------------------

        vlayout3 = QVBoxLayout()
        self.webInfoLabel = label_3 = QLabel("Web Support Information")
        self.webInfoLabel.setAccessibleName("aboutwebsupportinformation")
        label_3.setProperty('class', 'label-LeftCls')

        hlayout3_1 = QHBoxLayout()
        self.websiteLabel = label_3_1 = QLabel("Website")
        self.websiteLabel.setAccessibleName("aboutwebsite")
        label_3_1.setProperty('class', 'About-label-LeftCls')
        label_3_1.setAlignment(Qt.AlignTop)
        self.label_3_2 = QLabel()
        self.label_3_2.setAccessibleName("aboutwebsitelink")
        self.label_3_2.setOpenExternalLinks(True)
        self.label_3_2.setProperty('class', 'link')
        self.label_3_2.setWordWrap(True)

        hlayout3_1.addWidget(label_3_1)
        hlayout3_1.addWidget(self.label_3_2)
        hlayout3_1.addStretch(1)

        hlayout3_2 = QHBoxLayout()
        self.productsLabel = label_3_3 = QLabel("Products")
        self.productsLabel.setAccessibleName("aboutproducts")
        label_3_3.setProperty('class', 'About-label-LeftCls')
        label_3_3.setAlignment(Qt.AlignTop)
        self.label_3_4 = QLabel()
        self.label_3_4.setAccessibleName("aboutproductslink")
        self.label_3_4.setOpenExternalLinks(True)
        self.label_3_4.setProperty('class', 'link')
        self.label_3_4.setWordWrap(True)

        hlayout3_2.addWidget(label_3_3)
        hlayout3_2.addWidget(self.label_3_4)
        hlayout3_2.addStretch(1)

        hlayout3_3 = QHBoxLayout()
        self.contactLabel = label_3_5 = QLabel("Contacts")
        self.contactLabel.setAccessibleName("aboutcontacts")
        label_3_5.setProperty('class', 'About-label-LeftCls')
        label_3_5.setAlignment(Qt.AlignTop)
        self.label_3_6 = QLabel()
        self.label_3_6.setAccessibleName("aboutcontactslink")
        self.label_3_6.setOpenExternalLinks(True)
        self.label_3_6.setProperty('class', 'link')
        self.label_3_6.setWordWrap(True)

        hlayout3_3.addWidget(label_3_5)
        hlayout3_3.addWidget(self.label_3_6)
        hlayout3_3.addStretch(1)

        vlayout3.addWidget(label_3)
        vlayout3.addLayout(hlayout3_1)
        vlayout3.addLayout(hlayout3_2)
        vlayout3.addLayout(hlayout3_3)

        #  ----------------------separator----------------------

        vlayout4 = QVBoxLayout()
        now = datetime.datetime.now()
        label_4 = QLabel("Copyright© 2018-" + str(now.year) +", Cyber Power Systems, Inc. All rights reserved.")
        label_4.setAccessibleName("aboutcopyright")
        vlayout4.addWidget(label_4)
        label_4.setProperty('class', 'Copyright')

        #  ----------------------separator----------------------
        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(vlayout1)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vlayout2)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vlayout3)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vlayout4)
        configGroup.setLayout(serverLayoutAll)
        serverLayoutAll.addStretch(0)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        # 2019/02/23 Kenneth Setting for line-height
        serverLayoutAll.setSpacing(6)

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
        # mainLayout.addWidget(configGroup)

        self.renderText()
        self.setLayout(mainLayout)

    @property
    def check_update_signal(self):
        return self._check_update_signal

    @check_update_signal.setter
    def check_update_signal(self, value):
        self._check_update_signal = value

    @property
    def run_update_signal(self):
        return self._run_update_signal

    @run_update_signal.setter
    def run_update_signal(self, value):
        self._run_update_signal = value

    @property
    def run_restore_signal(self):
        return self._run_restore_signal

    @run_restore_signal.setter
    def run_restore_signal(self, value):
        self._run_restore_signal = value

    def renderText(self):
        self.versionLabel.setText(self.getTranslateString(i18nId.i18nId().version) + " " + systemDefine.pppeVersion)
        self.hardwareInfoLabel.setText(self.getTranslateString(i18nId.i18nId().Hardware_Information))
        self.modelNameLabel.setText(self.getTranslateString(i18nId.i18nId().Model_Name))
        self.serial_number_label.setText(self.getTranslateString(i18nId.i18nId().Serial_Number))
        self.firmVersionLabel.setText(self.getTranslateString(i18nId.i18nId().Firmware_Version))
        self.powerRatingLabel.setText(self.getTranslateString(i18nId.i18nId().Power_Ratting))
        self.webInfoLabel.setText(self.getTranslateString(i18nId.i18nId().Web_Support_Information))
        self.websiteLabel.setText(self.getTranslateString(i18nId.i18nId().website))
        self.productsLabel.setText(self.getTranslateString(i18nId.i18nId().Products))
        self.contactLabel.setText(self.getTranslateString(i18nId.i18nId().Contacts))

        urlLink1 = "<a style='color:red;' class='link' href=\"" + appLocaleData.appLocaleData().en_US_website_url + "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_the_technical_support_information_on_the_Web) + "</a>"
        self.label_3_2.setText(urlLink1)

        urlLink2 = "<a style='color:red;' class='link' href=\"" + appLocaleData.appLocaleData().en_US_products_url + "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_other_products_on_the_Web) + "</a>"
        self.label_3_4.setText(urlLink2)

        urlLink3 = "<a style='color:red;' class='link' href=\"" + appLocaleData.appLocaleData().en_US_contacts_url + "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_contact_information_on_the_Web) + "</a>"
        self.label_3_6.setText(urlLink3)
        # 2019/02/23 Kenneth
        #self.label_3_6.setWordWrap(True)

        self.check_update_btn.setText(self.getTranslateString(i18nId.i18nId().Check_for_Updates))
        self.update_now_btn.setText(self.getTranslateString(i18nId.i18nId().Update_Now))

        update_version = ""
        if self.update_status_data:
            if self.update_status_data.last_version:
                update_version = self.update_status_data.last_version
        self.update_now_label.setText(
            self.getTranslateString(i18nId.i18nId().New_Version_is_Available.format(update_version)))

        self.displayDataI18n()

    def ChangeUrlLinkBylocale(self, localeStr):

        urlLink1 = "<a style='color:red;' class='link' href=\""
        urlLink2 = "<a style='color:red;' class='link' href=\""
        urlLink3 = "<a style='color:red;' class='link' href=\""

        if localeStr == appLocaleData.appLocaleData().en_US:
            urlLink1 += appLocaleData.appLocaleData().en_US_website_url
            urlLink2 += appLocaleData.appLocaleData().en_US_products_url
            urlLink3 += appLocaleData.appLocaleData().en_US_contacts_url

        elif localeStr == appLocaleData.appLocaleData().de_DE:
            urlLink1 += appLocaleData.appLocaleData().de_DE_website_url
            urlLink2 += appLocaleData.appLocaleData().de_DE_products_url
            urlLink3 += appLocaleData.appLocaleData().de_DE_contacts_url

        elif localeStr == appLocaleData.appLocaleData().ja_JP:
            urlLink1 += appLocaleData.appLocaleData().ja_JP_website_url
            urlLink2 += appLocaleData.appLocaleData().ja_JP_products_url
            urlLink3 += appLocaleData.appLocaleData().ja_JP_contacts_url

        elif localeStr == appLocaleData.appLocaleData().cs_CZ:
            urlLink1 += appLocaleData.appLocaleData().cs_CZ_website_url
            urlLink2 += appLocaleData.appLocaleData().cs_CZ_products_url
            urlLink3 += appLocaleData.appLocaleData().cs_CZ_contacts_url

        elif localeStr == appLocaleData.appLocaleData().pl:
            urlLink1 += appLocaleData.appLocaleData().pl_website_url
            urlLink2 += appLocaleData.appLocaleData().pl_products_url
            urlLink3 += appLocaleData.appLocaleData().pl_contacts_url

        elif localeStr == appLocaleData.appLocaleData().es_ES:
            urlLink1 += appLocaleData.appLocaleData().es_ES_website_url
            urlLink2 += appLocaleData.appLocaleData().es_ES_products_url
            urlLink3 += appLocaleData.appLocaleData().es_ES_contacts_url

        else:
            urlLink1 += appLocaleData.appLocaleData().en_US_website_url
            urlLink2 += appLocaleData.appLocaleData().en_US_products_url
            urlLink3 += appLocaleData.appLocaleData().en_US_contacts_url

        urlLink1 += "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_the_technical_support_information_on_the_Web) + "</a>"
        urlLink2 += "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_other_products_on_the_Web) + "</a>"
        urlLink3 += "\">" + self.getTranslateString(
            i18nId.i18nId().Click_here_to_get_contact_information_on_the_Web) + "</a>"

        self.label_3_2.setText(urlLink1)
        self.label_3_4.setText(urlLink2)
        self.label_3_6.setText(urlLink3)

    def updatePage(self, updateData):
        self.displayData = updateData
        self.displayDataI18n()

    def updatePageWithSocket(self, updateData):
        self.displayData = updateData
        self.displayDataI18n()

    def displayDataI18n(self):
        if self.displayData.modelName == systemDefine.unknownStr:
            self.modelNameValue.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.modelNameValue.setText(self.displayData.modelName)

        if self.displayData.serialNumber == systemDefine.unknownStr:
            self.serial_number_value.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.serial_number_value.setText(self.displayData.serialNumber)

        if self.displayData.firmwareVer == systemDefine.unknownStr:
            self.firmVersionValue.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.firmVersionValue.setText(self.displayData.firmwareVer)

        powerRatingStr = ""
        if isinstance(self.displayData.apparentPower,int) and self.displayData.apparentPower > 0:
            powerRatingStr += str(self.displayData.apparentPower)
        else:
            powerRatingStr += systemDefine.noneValueStr

        powerRatingStr += " VA / "

        if isinstance(self.displayData.activePower,int) and self.displayData.activePower > 0:
            powerRatingStr += str(self.displayData.activePower)
        else:
            powerRatingStr += systemDefine.noneValueStr

        powerRatingStr += " " + self.getTranslateString(i18nId.i18nId().Watts)

        self.powerRatingValue.setText(powerRatingStr)

    def check_update(self):
        self.check_update_signal.emit(None)

    def check_update_result(self, data):
        if data.check_data:
            self.update_status_data = data
            if data.last_version:
                self.update_now_label.setText(
                    self.getTranslateString(i18nId.i18nId().New_Version_is_Available).format(data.last_version))
                self.update_now_group.show()
                if data.show_dialog:
                    self.show_software_update_dialog()
            else:
                if data.show_dialog:
                    self.show_software_up_to_date_dialog()
        else:
            if data.show_dialog:
                self.show_update_error_dialog(self.getTranslateString(i18nId.i18nId().Check_Update_Internet_Failed))

    def run_software_update(self):
        self.show_software_update_dialog()

    def software_update_dialog_result(self, type):
        if self.update_processing_dialog:
            self.update_processing_dialog.close()
            self.update_processing_dialog = None

        if self.restore_processing_dialog:
            self.restore_processing_dialog.close()
            self.restore_processing_dialog = None

        if type == "downloading_failed":
            self.show_update_error_dialog(self.getTranslateString(i18nId.i18nId().Error_Occurred_While_Downloading).replace("xxx1", "\n"))
        elif type == "updated_success":
            self.show_update_success_dialog(self.getTranslateString(i18nId.i18nId().Update_Successful))
        elif type == "updating_failed":
            self.show_update_error_dialog(self.getTranslateString(i18nId.i18nId().Error_Occurred_While_Updating).replace("xxx1", "\n"))
        elif type == "restored_success":
            self.show_restore_success_dialog(self.getTranslateString(i18nId.i18nId().Restore_Successful))
        elif type == "restored_failed":
            self.show_restore_error_dialog(self.getTranslateString(i18nId.i18nId().Error_Occurred_While_Restoring).replace("xxx1", "\n"))

    def show_software_update_dialog(self):
        dialog = SoftwareUpdateDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Update))
        dialog.setFixedWidth(400)
        dialog.exec()
        if dialog.result() == QDialog.Accepted:
            self.run_update_signal.emit(self.update_status_data)
            self.show_update_processing_dialog()

    def show_software_up_to_date_dialog(self):
        dialog = SoftwareUpToDateDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Update))
        dialog.setFixedWidth(400)
        dialog.exec()
        if dialog.result() == QDialog.Accepted:
            self.run_restore_signal.emit(None)
            self.show_restore_processing_dialog()


    def show_update_processing_dialog(self):
        dialog = UpdateProcessingDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Update))
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint |
             QtCore.Qt.CustomizeWindowHint
        )
        self.update_processing_dialog = dialog
        dialog.show()

    def show_restore_processing_dialog(self):
        dialog = RestoreProcessingDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Restore))
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint |
             QtCore.Qt.CustomizeWindowHint
        )
        self.restore_processing_dialog = dialog
        dialog.show()

    def show_update_success_dialog(self, msg=None):
        dialog = UpdateSuccessDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Update))
        if msg:
            dialog.set_message(msg)
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint
        )
        dialog.exec()

    def show_update_error_dialog(self, msg=None):
        dialog = UpdateErrorDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Update))
        if msg:
            dialog.set_message(msg)
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint
        )
        dialog.exec()

    def show_restore_success_dialog(self, msg=None):
        dialog = RestoreSuccessDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Restore))
        if msg:
            dialog.set_message(msg)
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint
        )
        dialog.exec()

    def show_restore_error_dialog(self, msg=None):
        dialog = RestoreErrorDialog(self)
        dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Software_Version_Restore))
        if msg:
            dialog.set_message(msg)
        dialog.setFixedWidth(340)
        dialog.setWindowFlags(
             QtCore.Qt.Window |
             QtCore.Qt.WindowSystemMenuHint |
             QtCore.Qt.WindowTitleHint
        )
        dialog.exec()

    class DisplayData:
        def __init__(self):
            self.modelName = systemDefine.unknownStr
            self.serialNumber = systemDefine.unknownStr
            self.firmwareVer = systemDefine.unknownStr
            self.apparentPower = 0
            self.activePower = 0

class CustumVersionLable(QLabel):
    def __init__(self, Text):
        QLabel.__init__(self)
        self.setText(Text)
        self.build_version = " ({0})".format(systemDefine.build_version)

    def enterEvent(self, QEvent):
        print("Mouse Enter Event")
        ver_name = self.text() + self.build_version
        self.setText(ver_name)

    def leaveEvent(self, QEvent):
        print("Mouse Leave Event")
        ver_name = self.text().replace(self.build_version, "")
        self.setText(ver_name)

class SoftwareUpdateDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        last_version = ""
        if parent.update_status_data.last_version:
            last_version = parent.update_status_data.last_version

        # 找到有可更新的版本
        update_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().New_Software_Version_Detected))
        update_label_1.setProperty('class', 'update_label_1')
        update_label_1.setWordWrap(True)

        hlayout_ver = QHBoxLayout()
        icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_download.png"), "upadate_icon", self)
        icon.setFixedWidth(20)
        icon.setFixedHeight(20)
        hlayout_ver.addWidget(icon)
        update_label_2 = QLabel(parent.getTranslateString(i18nId.i18nId().version) + " " + last_version)
        update_label_2.setProperty('class', 'update_label_2')
        hlayout_ver.addWidget(update_label_2)
        hlayout_ver.setAlignment(Qt.AlignCenter)
        hlayout_ver.setContentsMargins(0, 0, 0, 10)

        update_verison = QFrame()
        update_verison.setProperty('class', 'update_version')
        update_verison.setLayout(hlayout_ver)

        link_style = "<a style='color:#999999' class='link' href=\"" + systemDefine.PPP_DOWNLOAD_URL + "\">" + \
                     parent.getTranslateString(i18nId.i18nId().View_More_Information_About_This_Update) + "</a>"
        update_label_3 = QLabel(link_style)
        update_label_3.setProperty('class', 'update_label_3')
        update_label_3.setOpenExternalLinks(True)
        update_label_3.setWordWrap(True)

        hlayout_Btn = QHBoxLayout()
        self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Cancel))
        cancelBtn.setProperty('class', 'cancel_btn')
        cancelBtn.clicked.connect(self.dialog_reject_click)

        self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Apply))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_accept_click)

        hlayout_Btn.addWidget(self.cancelBtn)
        hlayout_Btn.addWidget(self.okBtn)
        hlayout_Btn.addStretch(1)

        layout = QVBoxLayout(self)

        layout.addWidget(update_label_1)
        layout.addWidget(update_verison)
        layout.addWidget(update_label_3)
        layout.addLayout(hlayout_Btn)
        layout.setContentsMargins(10, 0, 10, 0)

    def dialog_reject_click(self):
        self.reject()

    def dialog_accept_click(self):
        self.accept()

class SoftwareUpToDateDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # 目前為最新版本
        update_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Your_Software_is_Up_to_Date))
        update_label_1.setProperty('class', 'update_label_1')
        update_label_1.setWordWrap(True)

        hlayout_ver = QHBoxLayout()
        icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_uptodate.png"), "upadate_version", self)
        icon.setFixedWidth(20)
        icon.setFixedHeight(20)
        update_label_2 = QLabel(parent.getTranslateString(i18nId.i18nId().version) + systemDefine.pppeVersion)
        update_label_2.setProperty('class', 'update_label_2')
        hlayout_ver.addWidget(icon)
        hlayout_ver.addWidget(update_label_2)
        hlayout_ver.setAlignment(Qt.AlignCenter)

        update_verison = QFrame()
        update_verison.setProperty('class', 'update_version')
        update_verison.setLayout(hlayout_ver)

        update_label_3 = QLabel(parent.getTranslateString(i18nId.i18nId().Restoration))
        update_label_3.setProperty('class', 'update_label_3')

        update_checkbox_1 = QCheckBox(parent.getTranslateString(i18nId.i18nId().Restore_to_the_Previous_Software_Version))
        update_checkbox_1.setProperty('class', 'update_checkbox_1')
        update_checkbox_1.stateChanged.connect(self.restore_checkbox_statechanged_event)

        hlayout_Btn = QHBoxLayout()
        self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Cancel))
        cancelBtn.setProperty('class', 'cancel_btn')
        cancelBtn.clicked.connect(self.dialog_reject_click)

        self.applyBtn = applyBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Apply))
        applyBtn.setProperty('class', 'apply_btn')
        applyBtn.setEnabled(False)
        applyBtn.clicked.connect(self.dialog_accept_click)

        self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_reject_click)

        if self.show_restoration_checkbox():
            hlayout_Btn.addWidget(self.cancelBtn)
            hlayout_Btn.addWidget(self.applyBtn)
            hlayout_Btn.addStretch(1)
        else:
            hlayout_Btn.addWidget(self.okBtn)

        layout = QVBoxLayout(self)

        layout.addWidget(update_label_1)
        layout.addWidget(update_verison)
        if self.show_restoration_checkbox():
            layout.addWidget(update_label_3)
            layout.addWidget(update_checkbox_1)
        layout.addLayout(hlayout_Btn)
        layout.setContentsMargins(10, 0, 10, 0)

    def restore_checkbox_statechanged_event(self, state):
        if state == ViewData.CheckBoxState.checked.value:
            self.applyBtn.setEnabled(True)
        elif state == ViewData.CheckBoxState.unchecked.value:
            self.applyBtn.setEnabled(False)

    def dialog_reject_click(self):
        self.reject()

    def dialog_accept_click(self):
        self.accept()

    def show_restoration_checkbox(self):
        backup_version = None
        installer_path = settings.PROJECT_ROOT_PATH
        for file in os.listdir(installer_path):
            if 'backup_ppp' in file:
                backup_version = file.replace('backup_ppp', '')
                break

        now_version = systemDefine.pppeVersion
        if 'm' in now_version:
            now_version = now_version.replace('m', '')
        if 'DEMO' in now_version:
            now_version = now_version.replace(' DEMO', '')

        if backup_version is not None:
            if not now_version == backup_version:
                return True
            else:
                return False
        else:
            return False

class UpdateProcessingDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # gif圖片
        processing_movie = QMovie(os.path.join(settings.IMAGE_PATH, "icon_loading.gif"))
        processing_gif_label = QLabel()
        processing_gif_label.setMovie(processing_movie)
        processing_gif_label.setProperty('class', 'loading_image')
        processing_movie.start()

        processing_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Software_Is_Updating_Please_Wait))
        processing_label_1.setProperty('class', 'update_label_1')
        processing_label_1.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(processing_gif_label)
        layout.addWidget(processing_label_1)

class RestoreProcessingDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # gif圖片
        processing_movie = QMovie(os.path.join(settings.IMAGE_PATH, "icon_loading.gif"))
        processing_gif_label = QLabel()
        processing_gif_label.setMovie(processing_movie)
        processing_gif_label.setProperty('class', 'loading_image')
        processing_movie.start()

        processing_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Software_Is_Restoring_Please_Wait))
        processing_label_1.setProperty('class', 'update_label_1')
        processing_label_1.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(processing_gif_label)
        layout.addWidget(processing_label_1)

class UpdateSuccessDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        result_image = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_UpdateSuccess.png"), "result_image", self)
        result_image.setFixedHeight(80)
        self.result_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Update_Successful))
        self.result_label_1.setProperty('class', 'result_label_1')
        self.result_label_1.setWordWrap(True)

        hlayout_Btn = QHBoxLayout()

        okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_accept_click)

        hlayout_Btn.addWidget(okBtn)

        layout = QVBoxLayout(self)
        layout.addWidget(result_image)
        layout.addWidget(self.result_label_1)
        layout.addLayout(hlayout_Btn)

    def dialog_accept_click(self):
        self.accept()

    def set_message(self, msg):
        self.result_label_1.setText(msg)

class UpdateErrorDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        result_image = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_UpdateError.png"), "result_image", self)
        result_image.setFixedHeight(80)

        self.result_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Cloud_Error_Occurred))
        self.result_label_1.setProperty('class', 'result_label_1')
        self.result_label_1.setWordWrap(True)

        hlayout_Btn = QHBoxLayout()

        okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_accept_click)

        hlayout_Btn.addWidget(okBtn)

        layout = QVBoxLayout(self)
        layout.addWidget(result_image)
        layout.addWidget(self.result_label_1)
        layout.addLayout(hlayout_Btn)

    def dialog_accept_click(self):
        self.accept()

    def set_message(self, msg):
        self.result_label_1.setText(msg)

class RestoreSuccessDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        result_image = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_UpdateSuccess.png"), "result_image", self)
        result_image.setFixedHeight(80)
        self.result_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Restore_Successful))
        self.result_label_1.setProperty('class', 'result_label_1')
        self.result_label_1.setWordWrap(True)

        hlayout_Btn = QHBoxLayout()

        okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_accept_click)

        hlayout_Btn.addWidget(okBtn)

        layout = QVBoxLayout(self)
        layout.addWidget(result_image)
        layout.addWidget(self.result_label_1)
        layout.addLayout(hlayout_Btn)

    def dialog_accept_click(self):
        self.accept()

    def set_message(self, msg):
        self.result_label_1.setText(msg)

class RestoreErrorDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        result_image = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_UpdateError.png"), "result_image",
                                            self)
        result_image.setFixedHeight(80)

        self.result_label_1 = QLabel(parent.getTranslateString(i18nId.i18nId().Cloud_Error_Occurred))
        self.result_label_1.setProperty('class', 'result_label_1')
        self.result_label_1.setWordWrap(True)

        hlayout_Btn = QHBoxLayout()

        okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
        okBtn.setProperty('class', 'ok_btn')
        okBtn.clicked.connect(self.dialog_accept_click)

        hlayout_Btn.addWidget(okBtn)

        layout = QVBoxLayout(self)
        layout.addWidget(result_image)
        layout.addWidget(self.result_label_1)
        layout.addLayout(hlayout_Btn)

    def dialog_accept_click(self):
        self.accept()

    def set_message(self, msg):
        self.result_label_1.setText(msg)
