from enum import Enum

from PyQt5.QtCore import QDateTime, QSize
from PyQt5.QtGui import QPixmap, QMovie, QPainter, QFontMetrics
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDateTimeEdit, QWidget, QLabel, QFrame
import json

keepRunDDL = [5, 6, 7, 8]

class NaviMenu(Enum):
    Monitor_Module = 0
    Energy_Module = 1
    Configuration_Module = 2
    Information_Module = 3


class ConfigurationPageEnum(Enum):
    Schedule = 0
    Notification = 1
    Runtime = 2
    Voltage = 3
    SelfTest = 4
    Advanced = 5


class RuntimeSettingEnum(Enum):
    KeepComputerRunning = 0
    PreserveBatteryPower = 1


class ShutdownTypeEnum(Enum):
    Shutdown = 0
    Hibernation = 1


class InputVoltageSensitivity(Enum):
    Low = 0
    Medium = 1
    High = 2


class CO2MeasurementUnit(Enum):
    Kilograms = 0
    Pounds = 1

class UnitConversion (Enum):
    kg_to_lb = 2.204622
    lb_to_kg = 0.45359237

class UpsAlarmEnum(Enum):
    Disabled = 0
    Enabled = 1

class EventStatusLevel(Enum):
    Normal = 0
    Waring = 1
    Critical = 2
    Offline = 3

class EventCodeLevelStatus(Enum):
    Normal = 0
    Waring = 1
    Fault = 2

class LoginType(Enum):
    PowerPanelMobileLogin = 0
    PowerPanelMobileLogout = 1
    PowerPanelPersonalLogin = 2
    PowerPanelPersonalLogout = 3

class DeviceType(Enum):
    UPS = 0
    MobileDevice = 1

class ErrorCodeEventNumber(Enum):
    ID_HARDWARE_STATUS = 47
    ID_HARDWARE_STATUS_RESTORE = 134

class CheckBoxState(Enum):
    unchecked = 0
    partially_checked = 1
    checked = 2

class DateDialog(QDialog):
    def __init__(self, parent=None):
        super(DateDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.datetime = QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        self.datetime.setDisplayFormat("yyyy/MM/dd")
        layout.addWidget(self.datetime)
        layout.setContentsMargins(0, 0, 0, 0)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QDialog.Accepted)


class ImageWidget(QLabel):
    def __init__(self, imagePath, cls, parent):
        super(ImageWidget, self).__init__(parent)
        picture = QPixmap(imagePath)
        self.label = QLabel("", self)
        self.label.setPixmap(picture)
        self.label.setProperty("class", cls)


class ScheduleData:
    def __init__(self, jsonString=None):
        self.days = None
        self.onTimeHour = None
        self.onTimeMin = None
        self.onAction = None
        self.offTimeHour = None
        self.offTimeMin = None
        self.offAction = None
        self.noneReset = None
        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False)


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setProperty("class", "QHLineCls")

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
