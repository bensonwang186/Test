import sys
import traceback
from PyQt5 import QtCore

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QComboBox, QPushButton)

from System import systemDefine, systemFunction
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox

class Voltage(TemplatePage.TemplatePage):
    _setVoltageSignal = pyqtSignal(object)

    def __init__(self):
        super(Voltage, self).__init__()
        self.setAccessibleName("voltagepage")
        self.configGroup = None
        self.voltageMsgLabel = None
        self.voltageConfigTitleLabel = None
        self.voltageHighLabel = None
        self.voltageLowLabel = None
        self.currentVoltage = None
        self.upperLimitProp = None
        self.lowerLimitProp = None
        self.funcEnableFlag = False
        self.init_ui()

    @property
    def setVoltageSignal(self):
        return self._setVoltageSignal

    @setVoltageSignal.setter
    def setVoltageSignal(self, value):
        self._setVoltageSignal = value

    def init_ui(self):
        # <editor-fold desc="Current Status UI: Main data fields">

        self.configGroup = configGroup = QGroupBox("")
        configGroup.setObjectName("voltageQGroupBox")
        self.configGroup.setAccessibleName("voltagepagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setAccessibleName("voltagepagehelp")
        qMark.setProperty('class', 'qMark')
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("voltage.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        self.voltageMsgLabel = serverLabel_1 = QLabel()

        serverLabel_1.setFont(QFont("Roboto", 8, QFont.Bold))
        serverLabel_1.setProperty('class', 'label-LeftCls')

        serverLayout1 = QHBoxLayout()
        serverLayout1.addWidget(serverLabel_1)

        # <editor-fold desc="Radio Btn">

        vLayout1 = QVBoxLayout()
        self.voltageConfigTitleLabel = label0 = QLabel()
        label0.setProperty("class", "h3")
        vLayout1.addWidget(label0)

        hLayout1 = QHBoxLayout()
        self.voltageLowLabel = label1_1 = QLabel()
        self.lowerLimitDDL = lowerLimitDDL = ComboBox()
        self.lowerLimitDDL.setAccessibleName("voltagepagelowselect")
        self.lowerLimitDDL.activated.connect(lambda: self.setOutputVoltage(self.lowerLimitDDL))
        lowerLimitDDL.setProperty('class', 'runtimeRadioCls')
        self.label1_2 = QLabel()


        hLayout1.addWidget(label1_1)
        hLayout1.addWidget(lowerLimitDDL)
        hLayout1.addWidget(self.label1_2)
        hLayout1.addStretch(1)
        vLayout1.addLayout(hLayout1)

        """------------------------------------------Separator-------------------------------------------------------"""
        vLayout2 = QVBoxLayout()
        hLayout2 = QHBoxLayout()

        self.voltageHighLabel = label2_1 = QLabel()
        self.upperLimitDDL = upperLimitDDL = ComboBox()
        self.upperLimitDDL.setAccessibleName("voltagepagehignselect")
        self.upperLimitDDL.activated.connect(lambda: self.setOutputVoltage(self.upperLimitDDL))
        upperLimitDDL.setProperty('class', 'runtimeRadioCls')
        self.label2_2 = QLabel()

        self.interveneFuncDisplay()
        hLayout2.addWidget(label2_1)
        hLayout2.addWidget(upperLimitDDL)
        hLayout2.addWidget(self.label2_2)
        hLayout2.addStretch(1)
        vLayout2.addLayout(hLayout2)

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

    def interveneFuncDisplay(self):
        self.voltageConfigTitleLabel.setVisible(self.funcEnableFlag)
        self.voltageLowLabel.setVisible(self.funcEnableFlag)
        self.upperLimitDDL.setVisible(self.funcEnableFlag)
        self.label1_2.setVisible(self.funcEnableFlag)
        self.voltageHighLabel.setVisible(self.funcEnableFlag)
        self.lowerLimitDDL.setVisible(self.funcEnableFlag)
        self.label2_2.setVisible(self.funcEnableFlag)

    def updatePageWithSocket(self, updateData):
        try:
            upperLimitFlag = updateData.upperLimitList is not None and len(updateData.upperLimitList) > 0
            lowerLimitFlag = updateData.lowerLimitList is not None and len(updateData.lowerLimitList) > 0
            self.funcEnableFlag = upperLimitFlag and lowerLimitFlag
            self.interveneFuncDisplay()

            if self.funcEnableFlag:
                self.upperLimitDDL.clear()
                for item in updateData.upperLimitList:
                    self.upperLimitDDL.addItem(str(item), int(item))

                if systemFunction.intTryParse(updateData.upperLimitProperty) and int(updateData.upperLimitProperty) > -1:
                    index1 = self.upperLimitDDL.findText(str(updateData.upperLimitProperty), QtCore.Qt.MatchFixedString)
                    if index1 >= 0:
                        self.upperLimitDDL.setCurrentIndex(index1)

                    self.upperLimitProp = updateData.upperLimitProperty

                self.lowerLimitDDL.clear()
                for item in updateData.lowerLimitList:
                    self.lowerLimitDDL.addItem(str(item), int(item))

                if systemFunction.intTryParse(updateData.lowerLimitProperty) and int(updateData.lowerLimitProperty) > -1:
                    index2 = self.lowerLimitDDL.findText(str(updateData.lowerLimitProperty), QtCore.Qt.MatchFixedString)
                    if index2 >= 0:
                        self.lowerLimitDDL.setCurrentIndex(index2)

                    self.lowerLimitProp = updateData.lowerLimitProperty

            self.updateLabel()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def updateCurrentVoltage(self, deviceStatus):
        try:
            output_vol = systemDefine.noneValueStr
            if deviceStatus and not systemFunction.stringIsNullorEmpty(deviceStatus.OutputVolt):
                output_vol = round(systemFunction.stringParse2Float(deviceStatus.OutputVolt))

            self.currentVoltage = output_vol
            self.updateLabel()
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def updatePageByStatus(self, daemonStatus):
        disabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            pass

        elif daemonStatus and daemonStatus.deviceId == -1:
            pass

        elif daemonStatus and daemonStatus.deviceId != -1:
            disabledFlag = False

        self.lowerLimitDDL.setDisabled(disabledFlag)
        self.upperLimitDDL.setDisabled(disabledFlag)

    def updateLabel(self):

        lowerLimitPropStr = self.getTranslateString(i18nId.i18nId().none)
        if self.lowerLimitProp is not None:
            lowerLimitPropStr = str(self.lowerLimitProp)

        upperLimitPropStr = self.getTranslateString(i18nId.i18nId().none)
        if self.upperLimitProp is not None:
            upperLimitPropStr = str(self.upperLimitProp)

        lowerLimitStr = "<font color='red'>" + lowerLimitPropStr + "</font>"
        upperLimitStr = "<font color='red'>" + upperLimitPropStr + "</font>"
        wordingArr = self.getTranslateString(
            i18nId.i18nId().The_UPS_will_intervene_when_the_AC_utility_voltage_falls_below_xxxx_volts_or_rises_above_xxxx_volts).split(
            "xxxx")

        labelText = "<p style='line-height:18px;'>" \
                    + self.getTranslateString(i18nId.i18nId().The_current_voltage_is_xxxx_volts).replace("xxxx", str(self.currentVoltage))

        if self.funcEnableFlag:
            labelText += "<br>" + wordingArr[0] + lowerLimitStr + wordingArr[1] + upperLimitStr + wordingArr[2]
            labelText += "<br>" + self.getTranslateString(i18nId.i18nId().You_can_change_the_point_of_transfer_in_the_below_section)

        labelText +="</p>"

        self.voltageMsgLabel.setText(labelText)
        # 2019/02/23 Kenneth
        self.voltageMsgLabel.setWordWrap(True)

    def setOutputVoltage(self, b):
        param = int(b.currentData())

        if b == self.lowerLimitDDL:
            flag = True
            self.lowerLimitProp = param
        elif b == self.upperLimitDDL:
            flag = False
            self.upperLimitProp = param

        self.updateLabel()
        self._setVoltageSignal.emit((param, flag))

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Voltage))
        self.voltageConfigTitleLabel.setText(self.getTranslateString(i18nId.i18nId().UPS_will_intervene))

        wordingArr1 = self.getTranslateString(i18nId.i18nId().When_AC_utility_voltage_goes_above_xxxx_volts).split(
            "xxxx")
        self.voltageHighLabel.setText(wordingArr1[0])
        self.label1_2.setText(wordingArr1[1])

        wordingArr2 = self.getTranslateString(i18nId.i18nId().When_AC_utility_voltage_goes_below_xxxx_volts).split(
            "xxxx")
        self.voltageLowLabel.setText(wordingArr2[0])
        self.label2_2.setText(wordingArr2[1])

        self.updateLabel()

    class DisplayData:

        def __init__(self):
            self.currentVoltage = ""
            self.upperLimitProperty = ""
            self.lowerLimitProperty = ""
            self.upperLimitList = []
            self.lowerLimitList = []
