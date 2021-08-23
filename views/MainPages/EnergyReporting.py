import datetime

from PyQt5.QtCore import pyqtSignal, QDate
from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
                             QWidget, QDateTimeEdit, QPushButton)

from Utility.HelpOpener import HelpOpener
from views.Custom import ViewData
from views.Custom.CountryTableData import CountryTable
from i18n import i18nId
from views.MainPages import TemplatePage
from babel.numbers import format_decimal


class EnergyReporting(TemplatePage.TemplatePage):
    _energyReportingSignal = pyqtSignal(object)
    _energyReportingSettingSignal = pyqtSignal(object)
    _refreshSignal = pyqtSignal(object)

    def __init__(self):
        super(EnergyReporting, self).__init__()
        self.CountryTable = CountryTable().displayData
        self.setAccessibleName("energyreportpage")
        self.init_ui()

    @property
    def energyReportingSignal(self):
        return self._energyReportingSignal

    @energyReportingSignal.setter
    def energyReportingSignal(self, value):
        self._energyReportingSignal = value

    @property
    def energyReportingSettingSignal(self):
        return self._energyReportingSettingSignal

    @energyReportingSettingSignal.setter
    def energyReportingSettingSignal(self, value):
        self._energyReportingSettingSignal = value

    @property
    def refreshSignal(self):
        return self._refreshSignal

    @refreshSignal.setter
    def refreshSignal(self, value):
        self._refreshSignal = value

    def init_ui(self):
        # <editor-fold desc="Current Status UI: Main data fields">

        configGroup = QGroupBox("")
        configGroup.setObjectName("energyQGroupBox")
        configGroup.setAccessibleName("energyreportpagegroup")

        mainTitleLayout = QHBoxLayout()
        self.mainTitle = mainTitle = QLabel()
        mainTitle.setProperty('class', 'serverLabel_title')

        qMark = QPushButton("")
        qMark.setProperty('class', 'qMark')
        qMark.setAccessibleName("energyreportinghelp")
        qMark.clicked.connect(lambda: HelpOpener().openHelpDco("energyReport.htm"))

        mainTitleLayout.addWidget(mainTitle)
        mainTitleLayout.addWidget(qMark)
        mainTitleLayout.setProperty('class', 'main_title')

        self.label1 = QLabel("Statistics")
        self.label1.setProperty('class', 'label-LeftCls')

        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(self.label1)

        #  ----------------------separator----------------------

        hLayout2 = QHBoxLayout()
        self.label2 = QLabel()
        self.label2.setProperty('class', 'DateQLabel')
        self.label3 = QLabel()
        self.label3.setProperty('class', 'DateQLabel')

        now = datetime.datetime.now()

        self.startDate = startDate = QDateTimeEdit(self)
        startDate.setProperty('class', 'Date')
        startDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        startDate.setCalendarPopup(True)
        startDate.dateChanged.connect(self.onDateChanged)  # 設endDateEdit最小值
        startDate.setDisplayFormat("yyyy-MM-dd")
        startDate.setAccessibleName("startdate")


        # startDate.setDisabled(True)

        self.endDate = endDate = QDateTimeEdit(self)
        endDate.setProperty('class', 'Date')
        endDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        endDate.setCalendarPopup(True)
        endDate.dateChanged.connect(self.onDateChanged)  # 設endDateEdit最小值
        endDate.setDisplayFormat("yyyy-MM-dd")
        endDate.setAccessibleName("enddate")
        # endDate.setDisabled(True)

        hLayout2.addWidget(self.label2)
        hLayout2.addWidget(startDate)
        hLayout2.addWidget(self.label3)
        hLayout2.addWidget(endDate)
        hLayout2.addStretch(1)
        hLayout2.setContentsMargins(0, 0, 0, 0)

        #  ----------------------separator----------------------
        vLayout1 = QVBoxLayout()
        hLayout3 = QHBoxLayout()
        hLayout4 = QHBoxLayout()
        hLayout5 = QHBoxLayout()
        hLayout6 = QHBoxLayout()

        self.label4 = QLabel("Average Energy Consumption")
        self.label4.setProperty('class', 'Energy-label-LeftCls')
        self.avgEnergyConsumption = avgEnergyConsumption = QLabel("-- Wh")
        avgEnergyConsumption.setProperty('class', 'Energy-label-RightCls')
        hLayout3.addWidget(self.label4)
        hLayout3.addWidget(avgEnergyConsumption)

        self.label6 = QLabel("Cumulative Energy")
        self.label6.setProperty('class', 'Energy-label-LeftCls')
        self.cumulativeEnergy = cumulativeEnergy = QLabel("-- kWh")
        cumulativeEnergy.setProperty('class', 'Energy-label-RightCls')
        hLayout4.addWidget(self.label6)
        hLayout4.addWidget(cumulativeEnergy)

        self.label8 = QLabel("Cumulative Cost")
        self.label8.setProperty('class', 'Energy-label-LeftCls')
        self.cumulativeCost = cumulativeCost = QLabel("--")
        cumulativeCost.setProperty('class', 'Energy-label-RightCls')
        hLayout5.addWidget(self.label8)
        hLayout5.addWidget(cumulativeCost)

        self.label10 = QLabel("CO2")
        self.label10.setProperty('class', 'Energy-label-LeftCls')
        self.co2Emitted = co2Emitted = QLabel("--")
        co2Emitted.setProperty('class', 'Energy-label-RightCls')
        hLayout6.addWidget(self.label10)
        hLayout6.addWidget(co2Emitted)

        vLayout1.addLayout(hLayout3)
        vLayout1.addLayout(hLayout4)
        vLayout1.addLayout(hLayout5)
        vLayout1.addLayout(hLayout6)

        #  ----------------------separator----------------------

        serverLayoutAll = QVBoxLayout()
        serverLayoutAll.addLayout(mainTitleLayout)
        serverLayoutAll.addLayout(hLayout1)
        serverLayoutAll.addLayout(hLayout2)
        serverLayoutAll.addLayout(vLayout1)
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
        self.renderText()
        self.setLayout(mainLayout)

    def showEvent(self, QShowEvent):
        now = datetime.datetime.now()
        self.startDate.clearMaximumDate()
        self.startDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.startDate.setMaximumDate(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.endDate.clearMaximumDate()
        self.endDate.setDateTime(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self.endDate.setMaximumDate(datetime.datetime.combine(now, datetime.datetime.min.time()))
        self._refreshSignal.emit(self)

    def reportingQuery(self):
        startDate = self.startDate.dateTime().toPyDateTime()
        endDate = self.endDate.dateTime().toPyDateTime()

        self.energyReportingSignal.emit((startDate, endDate))

    def updateEnergyStatistic(self, indexTuple):
        cumulativeEnergyConsumption = indexTuple[0]
        cumulativeCost = indexTuple[1]
        co2Emitted = indexTuple[2]
        setting = indexTuple[3]
        locale_code = self.CountryTable[setting.country].localeCode

        days = (self.endDate.date().toPyDate() - self.startDate.date().toPyDate()).days + 1

        if days <= 0:
            days = 1

        cumEnergyConsumptionWh = cumulativeEnergyConsumption  # Wh
        avgEnergyConsumption = round((cumEnergyConsumptionWh / days), 2)
        if avgEnergyConsumption > 1000:
            avgEnergyConsumption = avgEnergyConsumption / 1000
            self.avgEnergyConsumption.setText(format_decimal(round(avgEnergyConsumption, 2), locale=locale_code, format="#####0.0##") + " kWh")
        else:
            self.avgEnergyConsumption.setText(format_decimal(avgEnergyConsumption, locale=locale_code, format="#####0.0##") + " Wh")

        if cumulativeEnergyConsumption > 1000:
            cumulativeEnergyConsumption = cumulativeEnergyConsumption / 1000
            self.cumulativeEnergy.setText(format_decimal(round(cumulativeEnergyConsumption, 2), locale=locale_code, format="#####0.0##") + " kWh")
        else:
            self.cumulativeEnergy.setText(format_decimal(cumulativeEnergyConsumption, locale=locale_code, format="#####0.0##") + " Wh")
        if setting.country is not None:
            cumulativeCostStr = self.CountryTable[setting.country].currency
            cumulativeCostStr = cumulativeCostStr.replace("0.00", format_decimal(cumulativeCost, locale=locale_code, format="#####0.0##"))
            self.cumulativeCost.setText(cumulativeCostStr)

        if setting.measurement is not None:
            if setting.measurement == ViewData.CO2MeasurementUnit.Kilograms.value:
                self.co2Emitted.setText(format_decimal(co2Emitted, locale=locale_code, format="#####0.0##") + " kg")
            elif setting.measurement == ViewData.CO2MeasurementUnit.Pounds.value:
                self.co2Emitted.setText(format_decimal(co2Emitted, locale=locale_code, format="#####0.0##") + " lb")

    def onDateChanged(self):
        self.endDate.setMinimumDate(self.startDate.date().toPyDate())
        self.reportingQuery()

    def updatePageByStatus(self, daemonStatus):

        disabledFlag = True

        if daemonStatus and not daemonStatus.isDaemonStarted:
            pass

        elif daemonStatus and daemonStatus.deviceId == -1:
            disabledFlag = False

        elif daemonStatus and daemonStatus.deviceId != -1:
            disabledFlag = False

        self.startDate.setDisabled(disabledFlag)
        self.endDate.setDisabled(disabledFlag)

    def renderText(self):
        self.mainTitle.setText(self.getTranslateString(i18nId.i18nId().Energy_Reporting))
        self.label1.setText(self.getTranslateString(i18nId.i18nId().Statistic))
        self.label2.setText(self.getTranslateString(i18nId.i18nId().From))
        self.label3.setText(self.getTranslateString(i18nId.i18nId().To))
        self.label4.setText(self.getTranslateString(i18nId.i18nId().Average_Energy_Consumption))
        self.label6.setText(self.getTranslateString(i18nId.i18nId().Cumulative_Energy_Consumption))
        self.label8.setText(self.getTranslateString(i18nId.i18nId().Cumulative_Cost))
        self.label10.setText(self.getTranslateString(i18nId.i18nId().CO2))