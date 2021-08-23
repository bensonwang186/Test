import datetime
import os
import sys
import traceback
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QWidget, QLineEdit, QPushButton, QTableWidget, QAbstractItemView, QHeaderView,
                             QScrollArea, QTableWidgetItem, QDialog, QDateTimeEdit, QGridLayout)

from System import settings, systemFunction
from Utility.HelpOpener import HelpOpener
from model_Json.tables.EnergyCost import EnergyCost
from model_Json.tables.EnergyCost import EnergySetting
from views.Custom import ViewData
from views.Custom.CountryTableData import CountryTable
from i18n import i18nId
from views.MainPages import TemplatePage
from views.Custom.CustomPlatformWidget import ComboBox
from babel.numbers import format_decimal, parse_decimal

ERROR_MSG_STYLE = "color: #db232b; margin-top: 10px;"
SUCCESS_MSG_STYLE = "color: #1b44e8; margin-top: 10px;"


class EnergySettings(TemplatePage.TemplatePage):
    _setEnergySettingSignal = pyqtSignal(object)
    _refreshSignal = pyqtSignal(object)

    def __init__(self):
        super(EnergySettings, self).__init__()
        self.setAccessibleName("energysettingpage")
        self.tableData = []
        self.CountryTable = CountryTable().displayData
        self.countryDDL = None
        self.costInputText = None
        self.showEnergyHistoryBtn = None
        self.emitInput = None
        self.measurementDDL = None
        self.errorMsg = None
        self.btnCount = 0
        self.init_ui()
        self.energySetting = None
        self.applyFlag = False  # isApplyBtnClick判斷用

    @property
    def setEnergySettingSignal(self):
        return self._setEnergySettingSignal

    @setEnergySettingSignal.setter
    def setEnergySettingSignal(self, value):
        self._setEnergySettingSignal = value

    @property
    def refreshSignal(self):
        return self._refreshSignal

    @refreshSignal.setter
    def refreshSignal(self, value):
        self._refreshSignal = value

    def init_ui(self):
        # <editor-fold desc="Main data fields">
        self.locale_format = LocaleDecimalFormat()

        configGroup = QGroupBox("")
        configGroup.setObjectName("settingQGroupBox")
        configGroup.setAccessibleName("energysettingpagegroup")


        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setProperty('class', 'qMark')
        qMark.setAccessibleName("energysettinghelp")
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("energySettings.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')
        mainTitleLayout.addStretch(1)

        self.label1 = QLabel()
        self.label1.setProperty('class', 'label-LeftCls')
        self.label2 = QLabel()
        self.label2.setProperty('class', 'Energy-label-LeftCls')
        self.countryDDL = QCombo1 = ComboBox()
        self.countryDDL.setAccessibleName("energysettingcountryselect")
        # 2019/02/23 Kenneth
        self.countryDDL.setProperty('class', 'energysettingcountryselect')
        for item in self.CountryTable.items():
            QCombo1.addItem(item[1].country, str(item[1].countryCode))

        self.countryDDL.activated.connect(partial(self.countrySelectorOnChange))

        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(self.label2)
        hLayout1.addWidget(QCombo1)
        hLayout1.addStretch(1)

        vLayout1 = QVBoxLayout()
        vLayout1.addLayout(mainTitleLayout)
        vLayout1.addWidget(self.label1)
        vLayout1.addLayout(hLayout1)
        vLayout1.addStretch(1)

        #  ----------------------separator----------------------
        self.label3 = QLabel()
        self.label3.setProperty('class', 'label-LeftCls')

        hLayout2 = QHBoxLayout()
        self.label4 = label4 = QLabel()
        label4.setProperty('class', 'Energy-label-LeftCls')
        self.costInputText = QLineEdit("")
        self.costInputText.setAccessibleName("energysettingcostinput")

        regex1 = QRegExp("^[0-9]\\d{0,5}(?:\.\d{1,2})?\s*$")
        validator1 = QRegExpValidator(regex1)
        self.costInputText.setValidator(validator1)
        self.costInputText.editingFinished.connect(lambda: self.textchanged(self.costInputText))
        self.costInputText.textChanged.connect(lambda: self.isApplyBtnClick())
        self.showEnergyHistoryBtn = showEnergyHistoryBtn = QPushButton(self.getTranslateString(i18nId.i18nId().Show_energy_cost_history))
        self.showEnergyHistoryBtn.setAccessibleName("energysettingshowhistory")
        self.showEnergyHistoryBtn.setProperty('class', 'EnergyHistoryBtn')
        showEnergyHistoryBtn.clicked.connect(lambda: self.showEnergyCostHistory())

        # <editor-fold desc="設定table相關參數">

        self.costTable = QTableWidget(len(self.tableData), 3)
        # self.costTable.setHorizontalHeaderLabels(['Date', 'Cost per kWh', ''])
        self.costTable.setObjectName("energyCostTable")
        self.costTable.verticalHeader().setVisible(False)
        self.costTable.setFocusPolicy(0)
        self.costTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.costTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.costTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.costTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.costTable.horizontalHeader().setStretchLastSection(True)
        self.costTable.setAlternatingRowColors(True)
        self.costTable.setColumnWidth(0, 190)
        self.costTable.setColumnWidth(1, 297.5)
        self.costTable.setColumnWidth(2, 70)
        self.setHistoryCostTable()
        self.costTable.hide()

        # </editor-fold>

        hLayout2.addWidget(self.label4)
        hLayout2.addWidget(self.costInputText)
        hLayout2.addStretch(1)

        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(self.label3)
        vLayout2.addWidget(self.costTable)
        vLayout2.addLayout(hLayout2)
        vLayout2.addWidget(showEnergyHistoryBtn)
        vLayout2.addStretch(1)
        #  ----------------------separator----------------------
        self.label5 = QLabel()
        self.label5.setProperty('class', 'label-LeftCls')
        self.label6 = QLabel()
        self.label6.setProperty('class', 'Energy-label-LeftCls')
        self.label7 = QLabel()
        self.label7.setProperty('class', 'Energy-label-LeftCls')

        hLayout3 = QHBoxLayout()
        self.emitInput = emitInput = QLineEdit("")
        self.emitInput.setAccessibleName("energysettingco2emitinput")

        regex2 = QRegExp("^[0-9]\\d{0,5}(?:\.\d{1,3})?\s*$")
        validator2 = QRegExpValidator(regex2)
        emitInput.setValidator(validator2)
        emitInput.textChanged.connect(lambda: self.isApplyBtnClick())

        hLayout3.addWidget(self.label6)
        hLayout3.addWidget(emitInput)
        hLayout3.addStretch(1)

        hLayout4 = QHBoxLayout()
        self.measurementDDL = QCombo2 = ComboBox()
        self.measurementDDL.setAccessibleName("energysettingunitselect")
        # 2019/02/23 Kenneth
        self.measurementDDL.setProperty('class', 'energysettingunitselect')
        QCombo2.addItem("Kilograms(kg)", 0)
        QCombo2.addItem("Pounds(lb)", 1)
        self.measurementDDL.currentIndexChanged.connect(self.unitSelectorOnChange)

        hLayout4.addWidget(self.label7)
        hLayout4.addWidget(QCombo2)
        hLayout4.addStretch(1)

        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(self.label5)
        vLayout3.addLayout(hLayout3)
        vLayout3.addLayout(hLayout4)
        vLayout3.addStretch(1)

        #  ----------------------separator----------------------
        vLayout4 = QVBoxLayout()
        self.applyBtn = applyBtn = QPushButton()
        self.applyBtn.setAccessibleName("energysettingapply")
        self.applyBtn.setProperty('class', 'applyBtn')  # 按鈕不能點的時候用applyBtn
        self.applyBtn.setEnabled(False)
        self.applyBtn.clicked.connect(self.applyClick)
        vLayout4.addWidget(applyBtn)
        #  ----------------------separator----------------------

        errorMsgLayout = QVBoxLayout()
        self.errorMsg = QLabel("")
        self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)
        errorMsgLayout.addWidget(self.errorMsg)

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(vLayout1)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vLayout2)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vLayout3)
        serverLayoutAll.addLayout(errorMsgLayout)
        serverLayoutAll.addWidget(ViewData.QHLine())
        serverLayoutAll.addLayout(vLayout4)
        configGroup.setLayout(serverLayoutAll)
        serverLayoutAll.addStretch(1)
        serverLayoutAll.setContentsMargins(20, 20, 20, 0)
        serverLayoutAll.setSpacing(0)

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

    def showEvent(self, QShowEvent):
        self.errorMsg.setText("")
        self._refreshSignal.emit(None)
        self.applyFlag = True  # 設flag: 因showEvent在__init__後執行, 會造成isApplyBtnClick誤判, 故設此flag

    def setHistoryCostTable(self):

        try:
            dataLen = len(self.tableData)
            for i in range(self.costTable.rowCount()):
                self.costTable.removeRow(self.costTable.rowAt(i))

            self.btnArr = []
            for index, item in enumerate(self.tableData):
                if (index + 1) == len(self.tableData):
                    dateStr = item.startDate.strftime("%Y/%m/%d") + "~" + self.getTranslateString(i18nId.i18nId().Today)
                else:
                    dateStr = item.startDate.strftime("%Y/%m/%d") + "~" + item.endDate.strftime("%Y/%m/%d")
                self.costTable.insertRow(index)
                self.costTable.setItem(index, 0, QTableWidgetItem(dateStr))
                self.costTable.setItem(index, 1, QTableWidgetItem(self.locale_format.format_decimal(item.cost)))

                self.btnArr.append(index)

                delBtnFlag = dataLen > 1

                self.btnArr[index] = TableEdit(delBtnFlag)
                self.btnArr[index].editBtn.clicked.connect(partial(self.editClick, index))

                if delBtnFlag:
                    self.btnArr[index].deleteBtn.clicked.connect(partial(self.deleteClick, index))

                self.costTable.setCellWidget(index, 2, self.btnArr[index])

            self.costTable.setMinimumHeight((35 * (dataLen + 1)))
            # self.costTable.rowAt(-1)

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def disabledPage(self, disabled):
        # self.CountryTable.set
        self.hideEnergyCostHistory()
        self.countryDDL.setDisabled(disabled)
        self.costInputText.setDisabled(disabled)
        self.showEnergyHistoryBtn.setDisabled(disabled)
        self.emitInput.setDisabled(disabled)
        self.measurementDDL.setDisabled(disabled)

    def restoreSetting(self, settings):

        self.energySetting = settings
        settingWithoutCost = settings[0]
        settingCosts = settings[1]

        if settingWithoutCost.measurement is not None:
            if settingWithoutCost.measurement >= 0:
                self.measurementDDL.setCurrentIndex(settingWithoutCost.measurement)

        if systemFunction.stringIsNullorEmpty(settingWithoutCost.country) is False:
            mappingData = self.CountryTable[settingWithoutCost.country]
            self.locale_format.locale_code(mappingData.localeCode)
            self.setInputQRegExpValidator()

            ddlText = mappingData.country
            index1 = self.countryDDL.findText(ddlText, QtCore.Qt.MatchFixedString)
            if index1 >= 0:
                self.countryDDL.setCurrentIndex(index1)

            if settingWithoutCost.measurement is not None:
                if settingWithoutCost.measurement == ViewData.CO2MeasurementUnit.Kilograms.value:
                    if systemFunction.stringIsNullorEmpty(settingWithoutCost.co2EmittedKg) is False:
                        self.emitInput.setText(self.locale_format.format_decimal(settingWithoutCost.co2EmittedKg))
                    else:
                        self.emitInput.setText(self.locale_format.format_decimal(mappingData.co2EmittedKg))
                else:
                    if systemFunction.stringIsNullorEmpty(settingWithoutCost.co2EmittedLb) is False:
                        self.emitInput.setText(self.locale_format.format_decimal(settingWithoutCost.co2EmittedLb))
                    else:
                        self.emitInput.setText(self.locale_format.format_decimal(mappingData.co2EmittedLb))
            else:
                self.emitInput.setText(self.locale_format.format_decimal(mappingData.co2EmittedKg))  # 預設給kg值

        # 組history table
        self.tableData = []
        now = datetime.datetime.now().replace(hour=00, minute=00, second=00, microsecond=00)
        # for item in settingCosts:
        for index, item in enumerate(settingCosts):
            row = self.TableDisplay()
            row.startDate = item.startTime

            if (index + 1) == len(settingCosts):
                row.endDate = now
            else:
                row.endDate = item.endTime

            row.cost = item.cost
            self.tableData.append(row)

        self.setHistoryCostTable()

        lastCost = settingCosts[-1]

        if lastCost is not None:
            costStr = self.locale_format.format_decimal(lastCost.cost)
            self.costInputText.setText(costStr)

        # self.applyFlag = False
        self.applyBtn.setProperty('class', 'applyBtn')  # 按鈕不能點的時候用applyBtn
        self.applyBtn.setEnabled(False)
        self.applyBtn.style().polish(self.applyBtn)

    def countrySelectorOnChange(self):
        countrySelected = self.countryDDL.currentData()

        if countrySelected != self.energySetting[0].country:
            print("country changed")
            try:
                dialog = CountryChangedDialog(self)
                # dialog.setFixedSize(400, 240)
                dialog.setFixedWidth(400)
                dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Change_Country))
                dialog.exec()
                if dialog.result() == QDialog.Accepted:
                    self.setInputQRegExpValidator()
                    print('ok')
                else:
                    print('Cancelled')
                    self._refreshSignal.emit(None)
                dialog.deleteLater()

            except Exception:
                traceback.print_exc(file=sys.stdout)
        else:
            self._refreshSignal.emit(None)

    def unitSelectorOnChange(self, index):
        value_text = self.emitInput.text()

        if index == ViewData.CO2MeasurementUnit.Kilograms.value:
            if value_text is not "":
                # 單位轉換pound轉kilogram
                value_float = float(self.locale_format.parse_decimal(value_text)) * ViewData.UnitConversion.lb_to_kg.value
                value_locale = self.locale_format.format_decimal(value_float)
                self.emitInput.setText(value_locale)

        else:
            if value_text is not "":
                # 單位轉換kilogram轉pound
                value_float = float(self.locale_format.parse_decimal(value_text)) * ViewData.UnitConversion.kg_to_lb.value
                value_locale = self.locale_format.format_decimal(value_float)
                self.emitInput.setText(value_locale)

        self.isApplyBtnClick()

    def textchanged(self, btn):
        # self.isApplyBtnClick()

        if btn is self.costInputText:
            self.applyEnergyCostChange()
            self.setHistoryCostTable()

    def showEnergyCostHistory(self):
        self.btnCount += 1
        if self.btnCount % 2 == 1:
            self.showEnergyHistoryBtn.setText(self.getTranslateString(i18nId.i18nId().Hide_energy_cost_history))
            self.label4.hide()
            self.costInputText.hide()
            self.costTable.show()
            self.showEnergyHistoryBtn.setProperty('class', 'EnergyHistoryBtn')
            self.showEnergyHistoryBtn.style().polish(self.showEnergyHistoryBtn)

            if len(self.tableData) > 0:
                self.costInputText.setText(self.locale_format.format_decimal(self.tableData[-1].cost))

        else:
            self.hideEnergyCostHistory()

    def hideEnergyCostHistory(self):
        self.showEnergyHistoryBtn.setText(self.getTranslateString(i18nId.i18nId().Show_energy_cost_history))
        self.label4.show()
        self.costInputText.show()
        self.costTable.hide()
        self.showEnergyHistoryBtn.setProperty('class', 'EnergyHistoryBtn_active')
        self.showEnergyHistoryBtn.style().polish(self.showEnergyHistoryBtn)

        if len(self.tableData) > 0:
            self.costInputText.setText(self.locale_format.format_decimal(self.tableData[-1].cost))

    def editClick(self, index):
        try:
            self.tableIndex = index
            dialog = TableEditDialog(self)
            dialog.setFixedSize(400, 240)
            dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Edit_Record))
            dialog.exec()

            if dialog.result() == QDialog.Accepted:
                print('ok')
            else:
                print('Cancelled')
            dialog.deleteLater()

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def deleteClick(self, index):
        try:
            self.tableIndex = index
            dialog = TableDelDialog(self)
            # 2019/02/23 Kenneth
            dialog.setFixedSize(400, 220)
            dialog.setWindowTitle(self.getTranslateString(i18nId.i18nId().Delete_Record))
            dialog.exec()
            if dialog.result() == QDialog.Accepted:
                # print('Dialog open')
                pass
            else:
                # print('Cancelled')
                pass
            dialog.deleteLater()

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def isApplyBtnClick(self):
        if self.applyFlag:
            flag = True

            if systemFunction.stringIsNullorEmpty(self.countryDDL.currentData()):
                flag = False

            if systemFunction.stringIsNullorEmpty(str(self.measurementDDL.currentData())):
                flag = False

            if systemFunction.stringIsNullorEmpty(self.costInputText.text()):
                flag = False

            if systemFunction.stringIsNullorEmpty(self.emitInput.text()):
                flag = False

            if flag:
                self.applyBtn.setProperty('class', 'applyBtn_active')  # 按鈕可以點的時候用applyBtn_active
                self.applyBtn.setEnabled(True)

            else:
                self.applyBtn.setProperty('class', 'applyBtn')  # 按鈕不能點的時候用applyBtn
                self.applyBtn.setEnabled(False)

            self.applyBtn.style().polish(self.applyBtn)

    def applyClick(self):
        try:
            setting = EnergySetting()
            setting.country = self.countryDDL.currentData()
            setting.co2EmittedKg = float(self.locale_format.parse_decimal(self.emitInput.text()))
            setting.co2EmittedLb = float(self.locale_format.parse_decimal(self.emitInput.text()))
            setting.measurement = self.measurementDDL.currentData()

            costArr = []
            for row in self.tableData:
                cost = EnergyCost()
                cost.startTime = row.startDate
                cost.endTime = row.endDate
                cost.cost = row.cost
                costArr.append(cost)

            flag = self.checkCostValueBound()
            if flag:
                self._setEnergySettingSignal.emit((setting, costArr))

        except Exception:
            traceback.print_exc(file=sys.stdout)

    def checkCostValueBound(self):
        flag = all(0.0 <= float(row.cost) <= 100000.0 for row in self.tableData)
        if flag is False:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Cost_value_should_be_within_range))
        return flag

    def applyEnergyCostChange(self):
        costInputValue = float(self.locale_format.parse_decimal(self.costInputText.text()))
        lastRecord = self.tableData[-1]

        if costInputValue != lastRecord.cost:
            if len(self.tableData) >= 1:
                lastRecordStartTime = datetime.datetime(year=lastRecord.startDate.year,
                                                        month=lastRecord.startDate.month,
                                                        day=lastRecord.startDate.day)

                lastRecordEndTime = datetime.datetime(year=lastRecord.endDate.year, month=lastRecord.endDate.month,
                                                      day=lastRecord.endDate.day)
                # lastRecord.endDate = lastRecord.endDate - datetime.timedelta(days=1)

                newLastRecord = self.TableDisplay()
                now = datetime.datetime.now().replace(hour=00, minute=00, second=00, microsecond=00)

                # if lastRecordEndTime + datetime.timedelta(days=1) < now:
                if lastRecordStartTime != lastRecordEndTime and lastRecordEndTime == now:

                    # edit
                    lastRecord.endDate = lastRecord.endDate - datetime.timedelta(days=1)

                    newLastRecord.startDate = now
                    newLastRecord.endDate = now
                    newLastRecord.cost = costInputValue
                    self.tableData.append(newLastRecord)
                elif lastRecordStartTime == lastRecordEndTime and lastRecordEndTime == now:
                    # newLastRecord.startDate = now
                    lastRecord.cost = costInputValue

                    # newLastRecord.endDate = now
                    # newLastRecord.cost = costInput
                    # self.tableData.append(newLastRecord)

    def applyResult(self, result):
        if result:
            self.errorMsg.setStyleSheet(SUCCESS_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Apply_Success))
            self._refreshSignal.emit(self)  # refresh view
        else:
            self.errorMsg.setStyleSheet(ERROR_MSG_STYLE)
            self.errorMsg.setText(self.getTranslateString(i18nId.i18nId().Apply_Error))

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Energy_Settings))
        self.label1.setText(self.getTranslateString(i18nId.i18nId().Country_Selection))
        self.label2.setText(self.getTranslateString(i18nId.i18nId().Country))
        self.label3.setText(self.getTranslateString(i18nId.i18nId().Energy_Cost))
        self.label4.setText(self.getTranslateString(i18nId.i18nId().Cost_per_kWh))
        self.label5.setText(self.getTranslateString(i18nId.i18nId().CO2_Emissions))
        self.label6.setText(self.getTranslateString(i18nId.i18nId().CO2_Emitted_per_kWh))
        self.label7.setText(self.getTranslateString(i18nId.i18nId().Unit_of_Measurement))

        self.measurementDDL.setItemText(0, self.getTranslateString(i18nId.i18nId().Kilograms))
        self.measurementDDL.setItemText(1, self.getTranslateString(i18nId.i18nId().Pounds))

        self.costTable.setHorizontalHeaderLabels([self.getTranslateString(i18nId.i18nId().Date), self.getTranslateString(i18nId.i18nId().Cost_per_kWh), ''])
        self.applyBtn.setText(self.getTranslateString(i18nId.i18nId().Apply))
        self.setHistoryCostTable()

        if self.btnCount % 2 == 1:
            self.showEnergyHistoryBtn.setText(self.getTranslateString(i18nId.i18nId().Hide_energy_cost_history))
        else:
            self.showEnergyHistoryBtn.setText(self.getTranslateString(i18nId.i18nId().Show_energy_cost_history))

    def setInputQRegExpValidator(self):
        if "," in self.locale_format.format_decimal(0.1):
            regex1 = QRegExp("^[0-9]\\d{0,5}(?:\,\d{1,2})?\s*$")
            regex2 = QRegExp("^[0-9]\\d{0,5}(?:\,\d{1,3})?\s*$")
        else:
            regex1 = QRegExp("^[0-9]\\d{0,5}(?:\.\d{1,2})?\s*$")
            regex2 = QRegExp("^[0-9]\\d{0,5}(?:\.\d{1,3})?\s*$")

        validator1 = QRegExpValidator(regex1)
        self.costInputText.setValidator(validator1)

        validator2 = QRegExpValidator(regex2)
        self.emitInput.setValidator(validator2)

    class TableDisplay:
        def __init__(self):
            self.startDate = None
            self.endDate = None
            self.cost = None

class TableEdit(QWidget):
    def __init__(self, delBtnFlag, parent=None):
        super(TableEdit, self).__init__(parent)

        self.editBtn = editBtn = QPushButton("")
        self.editBtn.setProperty('class', 'editBtn')
        self.deleteBtn = deleteBtn = QPushButton("")
        self.deleteBtn.setProperty('class', 'deleteBtn')

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(editBtn)

        if delBtnFlag:
            layout.addWidget(deleteBtn)

        self.setLayout(layout)

class TableEditDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.locale_format = parent.locale_format

        try:
            rowData = parent.tableData[parent.tableIndex]

            hLayout = QHBoxLayout()
            self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Cancel))
            cancelBtn.setProperty('class', 'cancelBtn')
            cancelBtn.clicked.connect(self.dialogCancelClick)
            self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().OK))
            okBtn.clicked.connect(partial(self.dialogOkClick, parent))  # parent為上一層之EnergySettings class

            hLayout.addWidget(cancelBtn)
            hLayout.addWidget(okBtn)
            hLayout.addStretch(1)

            startLabel = QLabel(parent.getTranslateString(i18nId.i18nId().StartDate))
            startLabel.setProperty('class', 'Date-label-LeftCls')
            self.startDateEdit = startDateEdit = QDateTimeEdit(self)
            self.startDateEdit.setProperty('class', 'Date')
            startDateEdit.setCalendarPopup(True)
            startDateEdit.setDateTime(datetime.datetime.combine(rowData.startDate, datetime.datetime.min.time()))
            startDateEdit.setDateRange(rowData.startDate, rowData.endDate)
            startDateEdit.dateChanged.connect(self.onDateChanged)  # 設endDateEdit最小值
            startDateEdit.setDisplayFormat("yyyy-MM-dd")

            endLabel = QLabel(parent.getTranslateString(i18nId.i18nId().EndDate))
            endLabel.setProperty('class', 'Date-label-LeftCls')
            self.endDateEdit = endDateEdit = QDateTimeEdit(self)
            self.endDateEdit.setProperty('class', 'Date')
            endDateEdit.setCalendarPopup(True)
            endDateEdit.setDateTime(datetime.datetime.combine(rowData.endDate, datetime.datetime.min.time()))
            endDateEdit.setDateRange(rowData.startDate, rowData.endDate)
            endDateEdit.setDisplayFormat("yyyy-MM-dd")

            costLabel = QLabel(parent.getTranslateString(i18nId.i18nId().Cost_per_kWh))
            costLabel.setProperty('class', 'Date-label-LeftCls')
            self.costEdit = costEdit = QLineEdit(self.locale_format.format_decimal(rowData.cost))

            if "," in self.locale_format.format_decimal(0.1):
                regex = QRegExp("^[0-9]\\d{0,5}(?:\,\d{1,2})?\s*$")
            else:
                regex = QRegExp("^[0-9]\\d{0,5}(?:\.\d{1,2})?\s*$")
            validator = QRegExpValidator(regex)
            self.costEdit.setValidator(validator)

            layout = QGridLayout()
            layout.setObjectName("QGridBox")
            layout.addWidget(startLabel, 0, 0)
            layout.addWidget(startDateEdit, 0, 1)
            layout.addWidget(endLabel, 1, 0)
            layout.addWidget(endDateEdit, 1, 1)
            layout.addWidget(costLabel, 2, 0)
            layout.addWidget(costEdit, 2, 1)

            # Kenneth 07/10
            vlayout = QVBoxLayout(self)
            vlayout.addLayout(layout)
            vlayout.addLayout(hLayout)

            # layout.setSpacing(0)
            # layout.setContentsMargins(0,0,0,0)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def onDateChanged(self):
        self.endDateEdit.setMinimumDateTime(self.startDateEdit.dateTime().toPyDateTime())

    def dialogCancelClick(self):
        self.reject()

    def dialogOkClick(self, parent):

        thisRow = parent.tableData[parent.tableIndex]

        fixedThisRow = parent.TableDisplay()  # 另存
        fixedThisRow.startDate = thisRow.startDate
        fixedThisRow.endDate = thisRow.endDate
        fixedThisRow.cost = thisRow.cost

        if thisRow.startDate == self.startDateEdit.dateTime().toPyDateTime() and thisRow.endDate == self.endDateEdit.dateTime().toPyDateTime():  # 日期未變動, 更新同一筆資料
            if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                thisRow.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))
                parent.isApplyBtnClick()

        else:  # 日期變動, 新增資料(1筆--> 2筆)

            if self.startDateEdit.dateTime().toPyDateTime() == self.endDateEdit.dateTime().toPyDateTime():  # 起=迄

                if self.startDateEdit.dateTime().toPyDateTime() == fixedThisRow.endDate:

                    # 更新原資料
                    thisRow.endDate = self.endDateEdit.dateTime().toPyDateTime() - datetime.timedelta(days=1)

                    # 插入新資料
                    newRow = parent.TableDisplay()
                    newRow.startDate = self.startDateEdit.dateTime().toPyDateTime()
                    newRow.endDate = self.endDateEdit.dateTime().toPyDateTime()

                    if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                        newRow.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))

                    newindex = parent.tableIndex + 1
                    parent.tableData.insert(newindex, newRow)

                elif self.startDateEdit.dateTime().toPyDateTime() == fixedThisRow.startDate:

                    # 更新原資料
                    thisRow.startDate = self.endDateEdit.dateTime().toPyDateTime() + datetime.timedelta(days=1)

                    # 插入新資料
                    newRow = parent.TableDisplay()
                    newRow.startDate = self.startDateEdit.dateTime().toPyDateTime()
                    newRow.endDate = self.endDateEdit.dateTime().toPyDateTime()

                    if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                        newRow.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))

                    parent.tableData.insert(parent.tableIndex, newRow)

                parent.isApplyBtnClick()
            else:  # 起!=迄

                if fixedThisRow.startDate == self.startDateEdit.dateTime().toPyDateTime():
                    # 更新原資料
                    thisRow.endDate = self.endDateEdit.dateTime().toPyDateTime()

                    if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                        thisRow.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))

                    # 插入新資料
                    newRow = parent.TableDisplay()
                    newRow.startDate = self.endDateEdit.dateTime().toPyDateTime() + datetime.timedelta(days=1)
                    newRow.endDate = fixedThisRow.endDate
                    newRow.cost = fixedThisRow.cost
                    newindex = parent.tableIndex + 1
                    parent.tableData.insert(newindex, newRow)
                    parent.isApplyBtnClick()
                elif fixedThisRow.endDate == self.endDateEdit.dateTime().toPyDateTime():
                    # 更新原資料
                    thisRow.endDate = self.startDateEdit.dateTime().toPyDateTime() - datetime.timedelta(days=1)

                    # 插入新資料
                    newRow = parent.TableDisplay()
                    newRow.startDate = self.startDateEdit.dateTime().toPyDateTime()
                    newRow.endDate = fixedThisRow.endDate

                    if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                        newRow.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))

                    parent.tableData.insert((parent.tableIndex + 1), newRow)
                    parent.isApplyBtnClick()
                else:
                    # 插入新資料
                    newRow1 = parent.TableDisplay()
                    newRow1.startDate = fixedThisRow.startDate
                    newRow1.endDate = self.startDateEdit.dateTime().toPyDateTime() - datetime.timedelta(days=1)
                    newRow1.cost = float(fixedThisRow.cost)

                    newRow2 = parent.TableDisplay()
                    newRow2.startDate = self.startDateEdit.dateTime().toPyDateTime()
                    newRow2.endDate = self.endDateEdit.dateTime().toPyDateTime()
                    if systemFunction.floatTryParse(self.locale_format.parse_decimal(self.costEdit.text())):
                        newRow2.cost = float(self.locale_format.parse_decimal(self.costEdit.text()))

                    newRow3 = parent.TableDisplay()
                    newRow3.startDate = self.endDateEdit.dateTime().toPyDateTime() + datetime.timedelta(days=1)
                    newRow3.endDate = fixedThisRow.endDate
                    newRow3.cost = float(fixedThisRow.cost)

                    parent.tableData.pop(parent.tableIndex)  # 移除原element
                    parent.tableData.insert(parent.tableIndex, newRow1)
                    parent.tableData.insert((parent.tableIndex + 1), newRow2)
                    parent.tableData.insert((parent.tableIndex + 2), newRow3)
                    parent.isApplyBtnClick()

        parent.setHistoryCostTable()
        self.accept()

class TableDelDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_delete_alert.png"), "alert_imgBox", self)
        # 2019/02/23 Kenneth
        icon.setFixedHeight(80)
        noticeLabel = QLabel(parent.getTranslateString(i18nId.i18nId().Are_you_sure_to_remove_this_record))
        noticeLabel.setProperty('class', 'noticeLabel')

        hlayout_Btn = QHBoxLayout()
        self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().No))
        cancelBtn.setProperty('class', 'cancelBtn')
        cancelBtn.clicked.connect(self.dialogCancelClick)
        self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Yes))
        okBtn.clicked.connect(partial(self.dialogOkClick, parent))  # parent為上一層之EnergySettings class

        hlayout_Btn.addWidget(self.cancelBtn)
        hlayout_Btn.addWidget(self.okBtn)
        hlayout_Btn.addStretch(1)
        # hlayout_Btn.setProperty('class', 'hlayout_Btn')

        # Kenneth 07/10
        layout = QVBoxLayout(self)
        layout.addWidget(icon)
        layout.addWidget(noticeLabel)
        layout.addLayout(hlayout_Btn)
        # 2019/02/23 Kenneth
        layout.setContentsMargins(10, 0, 10, 0)
        # layout.addStretch(1)

    def dialogCancelClick(self):
        self.reject()

    def dialogOkClick(self, parent):
        try:
            thisRow = parent.tableData[parent.tableIndex]
            if parent.tableIndex == 0:  # 畫面上將刪除第一筆, 並合併下一筆資料
                nextRow = parent.tableData[(parent.tableIndex + 1)]
                nextRow.startDate = thisRow.startDate
                del parent.tableData[parent.tableIndex]
                parent.isApplyBtnClick()
            else:  # 其餘情況, 畫面上將將刪除該筆, 並合併上一筆資料
                previousRow = parent.tableData[(parent.tableIndex - 1)]
                previousRow.endDate = thisRow.endDate
                del parent.tableData[parent.tableIndex]
                parent.isApplyBtnClick()

            parent.setHistoryCostTable()
            self.accept()
        except Exception:
            traceback.print_exc(file=sys.stdout)

class CountryChangedDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.locale_format = parent.locale_format

        icon = ViewData.ImageWidget(os.path.join(settings.IMAGE_PATH, "icon_delete_alert.png"), "alert_imgBox", self)
        # 2019/02/23 Kenneth
        icon.setFixedHeight(100)
        noticeLabel1 = QLabel(parent.getTranslateString(i18nId.i18nId().Changing_the_country_will_reset_the_energy_settings))
        noticeLabel1.setProperty('class', 'noticeLabel')
        # 2019/02/23 Kenneth
        noticeLabel1.setWordWrap(True)

        noticeLabel2 = QLabel(parent.getTranslateString(i18nId.i18nId().Are_you_sure_to_continue))
        noticeLabel2.setProperty('class', 'noticeLabel2')

        hlayout_Btn = QHBoxLayout()
        self.cancelBtn = cancelBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().No))
        cancelBtn.setProperty('class', 'cancelBtn')
        cancelBtn.clicked.connect(partial(self.dialogCancelClick, parent))
        self.okBtn = okBtn = QPushButton(parent.getTranslateString(i18nId.i18nId().Yes))
        okBtn.clicked.connect(partial(self.dialogOkClick, parent))  # parent為上一層之EnergySettings class

        hlayout_Btn.addWidget(self.cancelBtn)
        hlayout_Btn.addWidget(self.okBtn)
        hlayout_Btn.addStretch(1)
        # hlayout_Btn.setProperty('class', 'hlayout_Btn')

        # Kenneth 07/10
        layout = QVBoxLayout(self)
        layout.addWidget(icon)
        layout.addWidget(noticeLabel1)
        layout.addWidget(noticeLabel2)
        layout.addLayout(hlayout_Btn)
        # 2019/02/23 Kenneth
        layout.setContentsMargins(10, 0, 10, 0)
        #layout.addStretch(1)

    def dialogCancelClick(self, parent):
        originalCountry = parent.energySetting[0].country
        mappingData = parent.CountryTable[originalCountry]
        ddlText = mappingData.country
        index1 = parent.countryDDL.findText(ddlText, QtCore.Qt.MatchFixedString)
        if index1 >= 0:
            parent.countryDDL.setCurrentIndex(index1)

        self.reject()

    def dialogOkClick(self, parent):
        try:
            countrySelected = parent.countryDDL.currentData()
            mappingData = parent.CountryTable[countrySelected]
            self.locale_format.locale_code(mappingData.localeCode)
            parent.costInputText.setText(self.locale_format.format_decimal(mappingData.cost))

            # 組history table

            if len(parent.tableData) > 0:
                startTime = parent.tableData[0].startDate
                endTime = parent.tableData[-1].endDate

                if startTime is not None and endTime is not None:
                    parent.tableData = []
                    row = parent.TableDisplay()
                    row.startDate = startTime
                    row.endDate = endTime
                    row.cost = mappingData.cost
                    parent.tableData.append(row)
                    parent.setHistoryCostTable()

            unitSelected = parent.measurementDDL.currentData()

            if unitSelected == ViewData.CO2MeasurementUnit.Kilograms.value:
                parent.emitInput.setText(self.locale_format.format_decimal(mappingData.co2EmittedKg))
            else:
                parent.emitInput.setText(self.locale_format.format_decimal(mappingData.co2EmittedLb))

            parent.isApplyBtnClick()
            self.accept()

        except Exception:
            traceback.print_exc(file=sys.stdout)

class LocaleDecimalFormat():
    def __init__(self):
        self._locale_code = "en_US"

    def locale_code(self, locale_code):
        self._locale_code = locale_code

    def format_decimal(self, value):
        if type(value) is float:
            return format_decimal(value, locale=self._locale_code, format="#####0.###")
        elif type(value) is str:
            if systemFunction.floatTryParse(value):
                floatValue = float(value)
                return format_decimal(floatValue, locale=self._locale_code, format="#####0.###")
            else:
                return None
        else:
            return None

    def parse_decimal(self, numStr):
        return parse_decimal(numStr, locale=self._locale_code)
