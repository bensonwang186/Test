import os

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QPushButton)

import views.Custom.ViewData
from System import settings, systemDefine
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.MainPages import TemplatePage
from i18n import appLocaleData


class ConfigrationMain(TemplatePage.TemplatePage):
    def __init__(self, masterPage):
        super(ConfigrationMain, self).__init__()
        self.setAccessibleName("configuremainpage")
        self.masterPage = masterPage
        self.configHeadLabel = None
        self.configMsgLabel = None
        self.scheduleSubLabel = None
        self.nontifySubLabel = None
        self.runtimeSubLabel = None
        self.voltSubLabel = None
        self.selfTestSubLabel = None
        self.advancedSubLabel = None
        self.init_ui()

    def init_ui(self):

        # <editor-fold desc="Header">

        hBoxLayout_Header = QHBoxLayout()
        self.configHeadLabel = labelHeader = QLabel("Configure your UPS")
        labelHeader.setProperty('class', 'serverLabel_title')
        # labelHeader.setObjectName('ConfigrationMainHeader')

        qMark = QPushButton("")
        qMark.setAccessibleName("configuremainpagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("configuration.htm"))

        hBoxLayout_Header.addWidget(labelHeader)
        hBoxLayout_Header.addWidget(qMark)
        # hBoxLayout_Header.setProperty('class', 'main_title')

        # </editor-fold>

        configGroup = QGroupBox("")
        configGroup.setObjectName("configMainQGroupBox")
        configGroup.setAccessibleName("configuremainpagegroup")

        # <editor-fold desc="UI整合">

        hBoxLayout_Content_0 = QHBoxLayout()
        self.configMsgLabel = label_Content_0 = QLabel(
            "You can configure the settings of PowerPanel to ensure optimun performance of the UPS.")
        hBoxLayout_Content_0.addWidget(label_Content_0)
        label_Content_0.setProperty('class', 'hBoxLayout_Content_0')
        # 2019/02/23 Kenneth
        label_Content_0.setWordWrap(True)

        pageEnum = views.Custom.ViewData.ConfigurationPageEnum
        hBoxLayout_Content_1 = QHBoxLayout()

        # <editor-fold desc="Button">

        self.scheduleBtn = QPushButton("")
        self.scheduleBtn.setAccessibleName("configuremainpageschedule")
        self.scheduleBtn.setDefault(True)
        self.scheduleBtn.setProperty('class', 'leftBtn')
        self.scheduleBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.Schedule.value))
        scheduleImg = os.path.join(settings.IMAGE_PATH, "list_Schedule.png")
        self.scheduleBtn.setIcon(QIcon(scheduleImg))
        self.scheduleBtn.setIconSize(QSize(270, 90))
        # self.scheduleBtn.setFlat(True)
        # self.scheduleBtn.setAutoFillBackground(True)

        #  ------------------------------------------Separator------------------------------------------

        self.notificationBtn = QPushButton("")
        self.notificationBtn.setAccessibleName("configuremainpagenotification")
        self.notificationBtn.setDefault(True)
        self.notificationBtn.setProperty('class', 'rightBtn')
        self.notificationBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.Notification.value))
        notificationImg = os.path.join(settings.IMAGE_PATH, "list_Notification.png")
        self.notificationBtn.setIcon(QIcon(notificationImg))
        self.notificationBtn.setIconSize(QSize(270, 90))

        #  ------------------------------------------Separator------------------------------------------

        self.runtimeBtn = QPushButton("")
        self.runtimeBtn.setAccessibleName("configuremainpageruntime")
        self.runtimeBtn.setDefault(True)
        self.runtimeBtn.setProperty('class', 'leftBtn')
        self.runtimeBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.Runtime.value))
        runtimeImg = os.path.join(settings.IMAGE_PATH, "list_Runtime.png")
        self.runtimeBtn.setIcon(QIcon(runtimeImg))
        self.runtimeBtn.setIconSize(QSize(270, 90))

        #  ------------------------------------------Separator------------------------------------------

        self.voltageBtn = QPushButton("")
        self.voltageBtn.setAccessibleName("configuremainpagevoltage")
        self.voltageBtn.setDefault(True)
        self.voltageBtn.setProperty('class', 'rightBtn')
        self.voltageBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.Voltage.value))
        voltageImg = os.path.join(settings.IMAGE_PATH, "list_Voltage.png")
        self.voltageBtn.setIcon(QIcon(voltageImg))
        self.voltageBtn.setIconSize(QSize(270, 90))

        #  ------------------------------------------Separator------------------------------------------

        self.selfTestBtn = QPushButton("")
        self.selfTestBtn.setAccessibleName("configuremainpageselftest")
        self.selfTestBtn.setDefault(True)
        self.selfTestBtn.setProperty('class', 'leftBtn')
        self.selfTestBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.SelfTest.value))
        selfTestImg = os.path.join(settings.IMAGE_PATH, "list_Self_Test.png")
        self.selfTestBtn.setIcon(QIcon(selfTestImg))
        self.selfTestBtn.setIconSize(QSize(270, 90))

        #  ------------------------------------------Separator------------------------------------------

        self.advancedBtn = QPushButton("")
        self.advancedBtn.setAccessibleName("configuremainpageadvanced")
        self.advancedBtn.setDefault(True)
        self.advancedBtn.setProperty('class', 'rightBtn')
        self.advancedBtn.clicked.connect(lambda: self.pageLink(self.scheduleBtn, pageEnum.Advanced.value))
        advancedImg = os.path.join(settings.IMAGE_PATH, "list_Advanced.png")
        self.advancedBtn.setIcon(QIcon(advancedImg))
        self.advancedBtn.setIconSize(QSize(270, 90))

        # </editor-fold>

        hBoxLayout_Content_1.addWidget(self.scheduleBtn)
        hBoxLayout_Content_1.addWidget(self.notificationBtn)
        # Kenneth 20170725 修改按鈕間距
        hBoxLayout_Content_1.addStretch(1)
        hBoxLayout_Content_1.setSpacing(0)
        hBoxLayout_Content_1.setContentsMargins(0, 0, 0, 0)

        hBoxLayout_Content_2 = QHBoxLayout()
        hBoxLayout_Content_2.addWidget(self.runtimeBtn)
        hBoxLayout_Content_2.addWidget(self.voltageBtn)
        # Kenneth 20170725 修改按鈕間距
        hBoxLayout_Content_2.addStretch(1)
        hBoxLayout_Content_2.setSpacing(0)
        hBoxLayout_Content_2.setContentsMargins(0, 0, 0, 0)

        hBoxLayout_Content_3 = QHBoxLayout()
        hBoxLayout_Content_3.addWidget(self.selfTestBtn)
        hBoxLayout_Content_3.addWidget(self.advancedBtn)
        # Kenneth 20170725 修改按鈕間距
        hBoxLayout_Content_3.addStretch(1)
        hBoxLayout_Content_3.setSpacing(0)
        hBoxLayout_Content_3.setContentsMargins(0, 0, 0, 0)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(hBoxLayout_Header)
        serverLayoutAll.addLayout(hBoxLayout_Content_0)
        serverLayoutAll.addLayout(hBoxLayout_Content_1)
        serverLayoutAll.addLayout(hBoxLayout_Content_2)
        serverLayoutAll.addLayout(hBoxLayout_Content_3)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        serverLayoutAll.setSpacing(0)
        # serverLayoutAll.setObjectName("configMainQGroupBox")

        # </editor-fold>

        configGroup.setLayout(serverLayoutAll)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(configGroup)

        self.renderText()

        self.setLayout(mainLayout)

    def btnstate(self):
        if self.selfTestBtn.isChecked():
            print("button pressed")
        else:
            print("button released")

    def whichbtn(self, b):
        print("clicked button is " + b.text())

    def pageLink(self, btn, page):
        configSubMenu = list(filter(lambda x: systemDefine.PAGE_CONFIG == x.property('name'),
                                    self.masterPage.tapStackedWidget.children()))[0]  # 子選單

        configSubMenu.setCurrentRow(page)

    def renderText(self):
        self.configHeadLabel.setText(self.getTranslateString(i18nId.i18nId().Configure_your_UPS))
        self.configMsgLabel.setText(self.getTranslateString(
            i18nId.i18nId().You_can_configure_the_settings_of_application_short_name_to_ensure_optimum_performance_of_the_UPS))

        self.configMsgLabel.setWordWrap(True)

    def ChangePhotoLinkBylocale(self, localeStr):

        if localeStr == appLocaleData.appLocaleData().en_US:
            scheduleImgPath = "list_Schedule.png"
            notificationImgPath = "list_Notification.png"
            runtimeImgPath = "list_Runtime.png"
            voltageImgPath = "list_Voltage.png"
            selfTestImgPath = "list_Self_Test.png"
            advancedImgPath = "list_Advanced.png"

        elif localeStr == appLocaleData.appLocaleData().de_DE:
            scheduleImgPath = "de_list_Schedule.png"
            notificationImgPath = "de_list_Notification.png"
            runtimeImgPath = "de_list_Runtime.png"
            voltageImgPath = "de_list_Voltage.png"
            selfTestImgPath = "de_list_Self_Test.png"
            advancedImgPath = "de_list_Advanced.png"

        elif localeStr == appLocaleData.appLocaleData().ja_JP:
            scheduleImgPath = "jp_list_Schedule.png"
            notificationImgPath = "jp_list_Notification.png"
            runtimeImgPath = "jp_list_Runtime.png"
            voltageImgPath = "jp_list_Voltage.png"
            selfTestImgPath = "jp_list_Self_Test.png"
            advancedImgPath = "jp_list_Advanced.png"

        elif localeStr == appLocaleData.appLocaleData().cs_CZ:
            scheduleImgPath = "cz_list_Schedule.png"
            notificationImgPath = "cz_list_Notification.png"
            runtimeImgPath = "cz_list_Runtime.png"
            voltageImgPath = "cz_list_Voltage.png"
            selfTestImgPath = "cz_list_Self_Test.png"
            advancedImgPath = "cz_list_Advanced.png"

        elif localeStr == appLocaleData.appLocaleData().pl:
            scheduleImgPath = "po_list_Schedule.png"
            notificationImgPath = "po_list_Notification.png"
            runtimeImgPath = "po_list_Runtime.png"
            voltageImgPath = "po_list_Voltage.png"
            selfTestImgPath = "po_list_Self_Test.png"
            advancedImgPath = "po_list_Advanced.png"

        elif localeStr == appLocaleData.appLocaleData().es_ES:
            scheduleImgPath = "sp_list_Schedule.png"
            notificationImgPath = "sp_list_Notification.png"
            runtimeImgPath = "sp_list_Runtime.png"
            voltageImgPath = "sp_list_Voltage.png"
            selfTestImgPath = "sp_list_Self_Test.png"
            advancedImgPath = "sp_list_Advanced.png"

        else:
            scheduleImgPath = "list_Schedule.png"
            notificationImgPath = "list_Notification.png"
            runtimeImgPath = "list_Runtime.png"
            voltageImgPath = "list_Voltage.png"
            selfTestImgPath = "list_Self_Test.png"
            advancedImgPath = "list_Advanced.png"

        scheduleImg = os.path.join(settings.IMAGE_PATH, scheduleImgPath)
        self.scheduleBtn.setIcon(QIcon(scheduleImg))

        notificationImg = os.path.join(settings.IMAGE_PATH, notificationImgPath)
        self.notificationBtn.setIcon(QIcon(notificationImg))

        runtimeImg = os.path.join(settings.IMAGE_PATH, runtimeImgPath)
        self.runtimeBtn.setIcon(QIcon(runtimeImg))

        voltageImg = os.path.join(settings.IMAGE_PATH, voltageImgPath)
        self.voltageBtn.setIcon(QIcon(voltageImg))

        selfTestImg = os.path.join(settings.IMAGE_PATH, selfTestImgPath)
        self.selfTestBtn.setIcon(QIcon(selfTestImg))

        advancedImg = os.path.join(settings.IMAGE_PATH, advancedImgPath)
        self.advancedBtn.setIcon(QIcon(advancedImg))

