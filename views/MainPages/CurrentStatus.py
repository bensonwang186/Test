from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QPushButton)

import model_Json
from System import systemDefine, systemFunction
from Utility.HelpOpener import HelpOpener
from i18n import i18nId
from views.MainPages import TemplatePage
from views.Custom.ViewData import EventCodeLevelStatus


class CurrentStatus(TemplatePage.TemplatePage):
    def __init__(self):
        super(CurrentStatus, self).__init__()

        self.configGroup = None
        self.electricalPowerLabel = None
        self.electricalPowerValue = systemDefine.unknownStr
        self.voltSuppliedLabel = None
        self.voltSuppliedValue = systemDefine.noneValueStr
        self.PowerConditionLabel = None
        self.PowerConditionValue = systemDefine.unknownStr
        self.capacityLabel = None
        self.capacityValue = systemDefine.noneValueStr
        self.batteryStatusLabel = None
        self.batteryStatusValue = systemDefine.unknownStr
        self.runtimeLabel = None
        self.runtimeValue = systemDefine.noneValueStr
        self.loadLabel = None
        self.loadValue = systemDefine.noneValueStr
        self.persent_load = systemDefine.noneValueStr
        self.outputOverload = ""
        self.hwStatusLabel = None
        self.hwStatusValue = None
        self.OutputPowerConditionLabel = None
        self.OutputPowerConditionValue = systemDefine.unknownStr

        self.setAccessibleName("currentstatuspage")
        self.init_ui()

    def init_ui(self):

        # <editor-fold desc="Current Status UI: Main data fields">

        # configGroup = QGroupBox("Current_Status")
        # self.configGroup = configGroup = QGroupBox(self.getTranslateString("Current Status"))
        self.configGroup = configGroup = QGroupBox()
        configGroup.setObjectName("statusQGroupBox")
        self.configGroup.setAccessibleName("currentstatuspagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel("Current Status")
        self.mainTitle.setAccessibleName("currentstatustitle")
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setProperty('class', 'qMark')
        qMark.setAccessibleName("currentstatushelp")
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("current_status.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        # serverLabel_1 = QLabel("Electrical_power_supplied")
        # self.serverLabel_1 = serverLabel_1 = QLabel(self.getTranslateString("Electrical power supplied by"))
        self.electricalPowerLabel = serverLabel_1 = QLabel()
        self.electricalPowerLabel.setAccessibleName("statuspowersuppliedby")
        serverLabel_1.setFont(QFont("Roboto", 8, QFont.Bold))
        serverLabel_1.setProperty('class', 'label-LeftCls')
        self.electrical_power_value = serverLabel_2 = QLabel(systemDefine.unknownStr)
        serverLabel_2.setProperty('class', 'label-RightCls')

        self.voltSuppliedLabel = serverLabe2_1 = QLabel()
        serverLabe2_1.setProperty('class', 'label-LeftCls')
        self.volt_supplied_value = serverLabe2_2 = QLabel(systemDefine.noneValueStr + systemDefine.voltsStr)
        serverLabe2_2.setProperty('class', 'label-RightCls')

        self.PowerConditionLabel = serverLabe3_1 = QLabel()
        serverLabe3_1.setProperty('class', 'label-LeftCls')
        self.power_condition_value = serverLabe3_2 = QLabel(systemDefine.unknownStr)
        serverLabe3_2.setProperty('class', 'label-RightCls')

        self.capacityLabel = serverLabe4_1 = QLabel()
        serverLabe4_1.setProperty('class', 'label-LeftCls')
        self.capacity_value = serverLabe4_2 = QLabel(systemDefine.noneValueStr + systemDefine.percentageStr)
        serverLabe4_2.setProperty('class', 'label-RightCls')

        self.batteryStatusLabel = serverLabe5_1 = QLabel()
        serverLabe5_1.setProperty('class', 'label-LeftCls')
        self.battery_status_value = serverLabe5_2 = QLabel(systemDefine.unknownStr)
        serverLabe5_2.setProperty('class', 'label-RightCls')

        self.runtimeLabel = serverLabe6_1 = QLabel()
        serverLabe6_1.setProperty('class', 'label-LeftCls')
        self.runtime_value = serverLabe6_2 = QLabel(systemDefine.noneValueStr + systemDefine.minuteStr)
        serverLabe6_2.setProperty('class', 'label-RightCls')

        self.loadLabel = serverLabe7_1 = QLabel()
        serverLabe7_1.setProperty('class', 'label-LeftCls')
        self.load_value = serverLabe7_2 = QLabel(systemDefine.noneValueStr + systemDefine.wattsStr)
        serverLabe7_2.setProperty('class', 'label-RightCls')

        self.hwStatusLabel = serverLabe8_1 = QLabel()
        serverLabe8_1.setProperty('class', 'label-LeftCls')
        self.hw_status_value = serverLabe8_2 = QLabel(systemDefine.noneValueStr)
        serverLabe8_2.setProperty('class', 'label-RightCls')

        self.OutputPowerConditionLabel = serverLabe9_1 = QLabel()
        serverLabe9_1.setProperty('class', 'label-LeftCls')
        self.output_power_condiction_value = serverLabe9_2 = QLabel(systemDefine.unknownStr)
        serverLabe9_2.setProperty('class', 'label-RightCls')


        self.hwStatusValue = systemDefine.noneValueStr

        serverLayout1 = QHBoxLayout()
        serverLayout1.addWidget(serverLabel_1)
        serverLayout1.addWidget(serverLabel_2)
        serverLayout1.addStretch(1)
        serverLayout2 = QHBoxLayout()
        serverLayout2.addWidget(serverLabe2_1)
        serverLayout2.addWidget(serverLabe2_2)
        serverLayout2.addStretch(1)
        serverLayout3 = QHBoxLayout()
        serverLayout3.addWidget(serverLabe3_1)
        serverLayout3.addWidget(serverLabe3_2)
        serverLayout3.addStretch(1)
        serverLayout4 = QHBoxLayout()
        serverLayout4.addWidget(serverLabe4_1)
        serverLayout4.addWidget(serverLabe4_2)
        serverLayout4.addStretch(1)
        serverLayout5 = QHBoxLayout()
        serverLayout5.addWidget(serverLabe5_1)
        serverLayout5.addWidget(serverLabe5_2)
        serverLayout5.addStretch(1)
        serverLayout6 = QHBoxLayout()
        serverLayout6.addWidget(serverLabe6_1)
        serverLayout6.addWidget(serverLabe6_2)
        serverLayout6.addStretch(1)
        serverLayout7 = QHBoxLayout()
        serverLayout7.addWidget(serverLabe7_1)
        serverLayout7.addWidget(serverLabe7_2)
        serverLayout7.addStretch(1)
        serverLayout8 = QHBoxLayout()
        serverLayout8.addWidget(serverLabe8_1)
        serverLayout8.addWidget(serverLabe8_2)
        serverLayout8.addStretch(1)
        serverLayout9 = QHBoxLayout()
        serverLayout9.addWidget(serverLabe9_1)
        serverLayout9.addWidget(serverLabe9_2)
        serverLayout9.addStretch(1)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(serverLayout1)
        serverLayoutAll.addLayout(serverLayout2)
        serverLayoutAll.addLayout(serverLayout3)
        serverLayoutAll.addLayout(serverLayout9)
        serverLayoutAll.addLayout(serverLayout4)
        serverLayoutAll.addLayout(serverLayout5)
        serverLayoutAll.addLayout(serverLayout6)
        serverLayoutAll.addLayout(serverLayout7)
        serverLayoutAll.addLayout(serverLayout8)
        configGroup.setLayout(serverLayoutAll)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        # serverLayoutAll.setSpacing(0)

        # </editor-fold>

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(configGroup)

        self.setLayout(mainLayout)
        self.renderText()

    def updatePage(self, deviceStatus):

        # powerFrom = systemDefine.unknownStr
        # full_charged = systemDefine.unknownStr
        # remain_runtime = systemDefine.noneValueStr
        # persent_load = systemDefine.noneValueStr
        # output_vol = systemDefine.noneValueStr
        # battery_capacity = systemDefine.noneValueStr
        # powerCondition = systemDefine.unknownStr
        # outputOverload = ""
        # loadWatt = ""
        if deviceStatus:
            if deviceStatus.deviceId != -1:
                if deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.UtilityPower.value:
                    self.electricalPowerValue = self.getTranslateString(i18nId.i18nId().AC_Utility_Power)
                elif deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.BatteryPower.value:
                    self.electricalPowerValue = self.getTranslateString(i18nId.i18nId().Battery)
                elif deviceStatus.PowerSourceStatus == model_Json.DeviceStatusData.OutputStatus.NoOutput.value:
                    self.electricalPowerValue = self.getTranslateString(i18nId.i18nId().No_Output)

                # --------------------------------------separator--------------------------------------

                if deviceStatus.BatteryStatus == model_Json.DeviceStatusData.BatteryStatus.Discharging.value:
                    self.batteryStatusValue = self.getTranslateString(i18nId.i18nId().Discharging)
                elif deviceStatus.BatteryStatus == model_Json.DeviceStatusData.BatteryStatus.FullCharge.value:
                    self.batteryStatusValue = self.getTranslateString(i18nId.i18nId().Fully_Charged)
                elif deviceStatus.BatteryStatus == model_Json.DeviceStatusData.BatteryStatus.Charging.value:
                    self.batteryStatusValue = self.getTranslateString(i18nId.i18nId().Charging)

                # --------------------------------------separator--------------------------------------

                if not systemFunction.stringIsNullorEmpty(deviceStatus.RemainingRuntime):
                    self.runtimeValue = round(systemFunction.stringParse2Min(deviceStatus.RemainingRuntime))

                if deviceStatus.LoadWatt is not None and deviceStatus.LoadWatt >= 0:
                    self.loadValue = ("%.0f" % deviceStatus.LoadWatt)

                if deviceStatus.PercentLoad is not None and deviceStatus.PercentLoad >= 0:
                    self.persent_load = "{:.0%}".format(deviceStatus.PercentLoad)

                if not systemFunction.stringIsNullorEmpty(deviceStatus.OutputVolt):
                    self.voltSuppliedValue = round(systemFunction.stringParse2Float(deviceStatus.OutputVolt))

                if not systemFunction.stringIsNullorEmpty(deviceStatus.BatteryCapacity):
                    self.capacityValue = "{0:.0f} %".format(systemFunction.stringParse2Float(deviceStatus.BatteryCapacity))

                if deviceStatus.OutputOverload:
                    self.outputOverload = self.getTranslateString(i18nId.i18nId().Overload)
                else:
                    self.outputOverload = ""

                # --------------------------------------separator--------------------------------------
                if deviceStatus.SelfTestFWErrFlag:
                    if deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.UtilityFailure.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Power_Outage)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.UtilityLow.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Under_Voltage)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.UtilityHigh.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Over_Voltage)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.FreqFailure.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Frequency_Failure)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.UtilityBoost.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Voltage_Boost)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.UtilityBucket.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Voltage_Buck)

                    elif deviceStatus.InputStatus == model_Json.DeviceStatusData.InputStatus.Normal.value:
                        self.PowerConditionValue = self.getTranslateString(i18nId.i18nId().Normal)

                # --------------------------------------separator--------------------------------------

                if deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.Buck.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Voltage_Buck)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.Boost.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Voltage_Boost)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.Overload.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Overload)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.NoOutput.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().No_Output)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.ManualBypass.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Manual_Bypass)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.Bypass.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Bypass)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.BypassOverload.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Bypass_Overload)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.BypassUPSAbnormal.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().UPS_Bypass_Abnormal)

                elif deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.UtilityPower.value or \
                        deviceStatus.OutputStatus == model_Json.DeviceStatusData.OutputStatus.BatteryPower.value:
                    self.OutputPowerConditionValue = self.getTranslateString(i18nId.i18nId().Normal)

                if deviceStatus.UpsEventFlag is not None:
                    self.hwStatusValue = deviceStatus.UpsEventFlag
        else:
            self.electricalPowerValue = systemDefine.unknownStr
            self.voltSuppliedValue = systemDefine.noneValueStr
            self.PowerConditionValue = systemDefine.unknownStr
            self.capacityValue = systemDefine.noneValueStr
            self.batteryStatusValue = systemDefine.unknownStr
            self.runtimeValue = systemDefine.noneValueStr
            self.loadValue = systemDefine.noneValueStr
            self.persent_load = systemDefine.noneValueStr
            self.outputOverload = ""
            self.OutputPowerConditionValue = systemDefine.unknownStr

        self.displayDataI18n()

    def displayDataI18n(self):
        label = self.findChildren(QLabel)

        if self.electricalPowerValue == systemDefine.unknownStr:
            self.electrical_power_value.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.electrical_power_value.setText(self.electricalPowerValue)

        if self.PowerConditionValue == systemDefine.unknownStr:
            self.power_condition_value.setText(str(self.getTranslateString(i18nId.i18nId().Unknown)))
        else:
            self.power_condition_value.setText(str(self.PowerConditionValue))

        if self.batteryStatusValue == systemDefine.unknownStr:
            self.battery_status_value.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.battery_status_value.setText(self.batteryStatusValue)

        self.volt_supplied_value.setText(str(self.voltSuppliedValue) + " " + self.getTranslateString(i18nId.i18nId().volts))
        self.capacity_value.setText(str(self.capacityValue))
        self.runtime_value.setText(str(self.runtimeValue) + " " + self.getTranslateString(i18nId.i18nId().minutes))

        if systemFunction.stringIsNullorEmpty(self.outputOverload):
            self.load_value.setText(str(self.loadValue) + " " + self.getTranslateString(i18nId.i18nId().watts))
        else:
            formatStr = "<font color='red'>{0} ({1} {2}) {3}</font>".format(str(self.persent_load), str(self.loadValue), self.getTranslateString(i18nId.i18nId().watts), self.outputOverload)
            self.load_value.setText(formatStr)

        if self.OutputPowerConditionValue == systemDefine.unknownStr:
            self.output_power_condiction_value.setText(self.getTranslateString(i18nId.i18nId().Unknown))
        else:
            self.output_power_condiction_value.setText(self.OutputPowerConditionValue)

        if self.hwStatusValue is not None:
            if self.hwStatusValue == EventCodeLevelStatus.Normal.value:
                self.hw_status_value.setText(self.getTranslateString(i18nId.i18nId().Normal))
            elif self.hwStatusValue == EventCodeLevelStatus.Waring.value:
                self.hw_status_value.setText(self.getTranslateString(i18nId.i18nId().Warning))
            elif self.hwStatusValue == EventCodeLevelStatus.Fault.value:
                self.hw_status_value.setText(self.getTranslateString(i18nId.i18nId().Fault))
        else:
            self.hw_status_value.setText(self.getTranslateString(i18nId.i18nId().Normal))

    def renderText(self):
        # self.configGroup.setTitle(self.getTranslateString(i18nId.i18nId().Current_Status))
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Current_Status))
        self.electricalPowerLabel.setText(self.getTranslateString(i18nId.i18nId().Electrical_power_supplied_by))
        self.voltSuppliedLabel.setText(self.getTranslateString(i18nId.i18nId().Voltage_supplied))
        self.PowerConditionLabel.setText(self.getTranslateString(i18nId.i18nId().Input_Power_Condition))
        self.capacityLabel.setText(self.getTranslateString(i18nId.i18nId().Remaining_battery_capacity))
        self.batteryStatusLabel.setText(self.getTranslateString(i18nId.i18nId().Battery_status))
        self.runtimeLabel.setText(self.getTranslateString(i18nId.i18nId().Remaining_battery_runtime))
        self.loadLabel.setText(self.getTranslateString(i18nId.i18nId().UPS_load))
        self.hwStatusLabel.setText(self.getTranslateString(i18nId.i18nId().hardware_status))
        self.OutputPowerConditionLabel.setText(self.getTranslateString(i18nId.i18nId().Output_Power_Condition))
        self.displayDataI18n()
