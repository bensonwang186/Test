import os
import webbrowser
import platform
from System import settings
from i18n.appLocaleData import appLocaleData as appLocaleData
from i18n.appLocaleData import appLocaleRecorder


class HelpOpener:

    def openHelpDco(self, page):
        lanFolder = "english"
        if appLocaleRecorder().appLocale == appLocaleData.en_US:
            lanFolder = "english"
        elif appLocaleRecorder().appLocale == appLocaleData.zh_CN:
            lanFolder = "chinese.prc"
        elif appLocaleRecorder().appLocale == appLocaleData.zh_TW:
            lanFolder = "chinese.taiwan"
        # elif appLocaleRecorder().appLocale == appLocaleData.cs_CZ:
        #     lanFolder = "czech"
        elif appLocaleRecorder().appLocale == appLocaleData.fr_FR:
            lanFolder = "french.canadian"
        elif appLocaleRecorder().appLocale == appLocaleData.de_DE:
            lanFolder = "german"
        elif appLocaleRecorder().appLocale == appLocaleData.hu_HU:
            lanFolder = "hungarian"
        elif appLocaleRecorder().appLocale == appLocaleData.it_IT:
            lanFolder = "italian"
        elif appLocaleRecorder().appLocale == appLocaleData.ja_JP:
            lanFolder = "japanese"
        # elif appLocaleRecorder().appLocale == appLocaleData.pl:
        #     lanFolder = "polish"
        elif appLocaleRecorder().appLocale == appLocaleData.ru:
            lanFolder = "russian"
        elif appLocaleRecorder().appLocale == appLocaleData.sl:
            lanFolder = "slovenian"
        # elif appLocaleRecorder().appLocale == appLocaleData.es_ES:
        #     lanFolder = "spanish"

        HELP_PATH = os.path.join(settings.PROJECT_ROOT_PATH, "help")
        HELP_DOC_PATH = os.path.join(HELP_PATH, lanFolder)
        HELP_DOC_FILE_PATH = os.path.join(HELP_DOC_PATH, page)

        if platform.system() == 'Windows':
            webbrowser.open(HELP_DOC_FILE_PATH)
        elif platform.system() == 'Darwin':
            webbrowser.open("file://" + HELP_DOC_FILE_PATH)
        else:
            webbrowser.open(HELP_DOC_FILE_PATH)
