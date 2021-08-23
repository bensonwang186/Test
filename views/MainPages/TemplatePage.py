import traceback

import PyQt5.QtCore
import sys
from PyQt5.QtWidgets import QWidget
from Utility import i18nTranslater
from i18n import appLocaleData

class TemplatePage(QWidget):
    def __init__(self):
        super(TemplatePage, self).__init__()
        self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorder().appLocale)

    def getTranslateString(self, id):
        return self.i18nTranslater.getTranslateString(id)

    def renderText(self):
        pass

    def reRender(self, localeStr):
        try:
            # self.i18nTranslater = i18nTranslater.i18nTranslater(appLocale.appLocale.list[self.testIndex])
            self.i18nTranslater = i18nTranslater.i18nTranslater(localeStr)
            self.renderText()

        except Exception:
            traceback.print_exc(file=sys.stdout)