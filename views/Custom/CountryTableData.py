import xml.etree.ElementTree as ET

from System import settings


class CountryTable:
    tree = ET.parse(settings.COUNTRY_TABLE_PATH)
    root = tree.getroot()
    data = root;

    def __init__(self):
        self.displayData = dict()
        self.parseXML()

    def parseXML(self):
        for child in self.root:
            display = DisplayData()

            countryCode = child.find("countryCode").text
            display.country = countryCode + " - " + child.get('name')
            display.countryCode = countryCode
            display.localeCode = child.find("localeCode").text
            display.cost = child.find("cost").text
            display.co2EmittedKg = child.find("co2EmittedKg").text
            display.co2EmittedLb = child.find("co2EmittedLb").text
            display.currency = child.find("currency").text
            self.displayData[countryCode] = display

        import collections
        self.displayData = collections.OrderedDict(sorted(self.displayData.items()))
        # print(od)

class DisplayData:
    def __init__(self):
        self.country = None
        self.countryCode = None
        self.localeCode = None
        self.cost = None
        self.co2EmittedKg = None
        self.co2EmittedLb = None
        self.currency = None

# dic = CountryTable().displayData
