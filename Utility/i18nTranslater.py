import gettext
import traceback

import sys

from System import settings
from i18n import appLocaleData, i18nId


class i18nTranslater(object):

    applicationShortName = "application_short_name"

    def __init__(self, loc):
        # current_locale, encode = localeVar
        try:
            self.trans = gettext.translation('messages', settings.I18N_PATH, [loc])
        except:
            # traceback.print_exc(file=sys.stdout)
            self.trans = gettext.translation('messages', settings.I18N_PATH, [appLocaleData.appLocaleData.en_US])

    def getTranslateString(self, key):
        mes = self.trans.gettext(key)
        if i18nTranslater.applicationShortName in mes:
            mes = mes.replace(i18nTranslater.applicationShortName, "PowerPanel")
        return mes


class MessageCoverter:

    # PREFIX = "eventDescription.eventId."
    PREFIX = "eventId_"
    PREFIX_EVENT_CODE = "eventCode_"

    def __init__(self):
        pass

    def coveterEventMessage(self, loc, eventId):
        eventDescriptorID = self.PREFIX + str(eventId)
        return i18nTranslater(loc).getTranslateString(eventDescriptorID)

    def coveterEventCodeMessage(self, loc, errCode):
        eventCodeDescriptorID = self.PREFIX_EVENT_CODE + str(errCode)
        if hasattr(i18nId.i18nId(), eventCodeDescriptorID):
            return i18nTranslater(loc).getTranslateString(getattr(i18nId.i18nId(), eventCodeDescriptorID))
        else:
            return ""