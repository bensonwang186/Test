from enum import Enum
from System import buildConfig


#  透過metaclass導入Singleton
class Singleton(object):
    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


class LoginType(Enum):
    PowerPanelMobileLogin = 0
    PowerPanelMobileLogout = 1
    PowerPanelPersonalLogin = 2
    PowerPanelPersonalLogout = 3


class DeviceType(Enum):
    UPS = 0
    MobileDevice = 1


class UPS_StateMobile(Enum):
    The_UPS_is_working_normally = 0
    PPPE_service_is_not_ready = 1
    Unable_to_establish_communication_with_UPS = 2
    Deactivate_PPP_mobile_solution = 3

class BuildConfiguration(Enum):
    Production = 0
    Test = 1

class TestResult(enumerate):
    TEST_PASSED = 1
    TEST_WARNING = 2
    TEST_ERROR = 3
    TEST_ABORTED = 4
    TEST_PROGRESSING = 5
    TEST_NOTHING = 6

class TestResultType(enumerate):
    TEST_RESULT = 1
    BATTERY_CALIBRATION_TEST_RESULT = 2

class TestType(enumerate):
    TEST_TYPE_NONE = 0
    TEST_TYPE_TEST = 1
    TEST_TYPE_CALIBRATE = 2

class CloudBatteryTestResult(enumerate):
    Passed = 0
    Waiting = 1
    Failed = 2
    NeverBeExecuted = 3

class CloudBatteryTestFrom(enumerate):
    SW_PPB = 0
    Web = 1
    App = 2
    SW_PPP = 3

class ExcutionMode(enumerate):
    DEV = 0
    PRODUCTION = 1

DEVICE_MONITOR_INTERVAL = 3  # sec
DEVICE_STATUS_MESSAGE_INTERVAL = 300  # sec
APNS_SILENCE_MESSAGE_INTERVAL = 30  # sec
APNS_SILENCE_MESSAGE_SEND_TIMES = 20  # times
APNS_LOST_COMMUNICATION_SILENCE_MESSAGE_SEND_DURATION = 60  # sec
EMQ_LOST_COMMUNICATION_MESSAGE_SEND_DURATION = 300  # sec

sideBarLabel_powerSourceStr = "Power Source"
sideBarLabel_batteryCapacityStr = "Battery Capacity"
sideBarLabel_estimatedRuntimeStr = "Estimated Runtime"

ACUtilityStr = "AC Utility"
BatteryStr = "Battery"

percentageStr = " %"
minStr = " min."
voltsStr = " volts"
wattsStr = " watts"
minuteStr = " minute"
unknownStr = "Unknown"
noneValueStr = "---"
dischargingStr = "Discharging"
fullChargedStr = "Full Charged"
chargingStr = "Charging"

ups_working_normallyStr = "The UPS is working normally."
pppe_notReadyStr = "PowerPanel® Personal Service is not ready."
ups_unable_communicationStr = "Unable to establish communication with UPS."

# Build Installer Configuration
BUILD_FOR = buildConfig.BUILD_FOR

pppeVersion = "2.3.1"

if BUILD_FOR is BuildConfiguration.Test.value:
    pppeVersion += " DEMO"

build_version = buildConfig.BUILD_VERSION

pppName = "CyberPower PowerPanel Personal"
iosLinkUrl = "https://itunes.apple.com/tw/app/powerpanel/id1342462532?l=en&mt=8"
androidLinkUrl = "https://play.google.com/store/apps/details?id=com.cyberpower.pppe"
POWERPANEL_CLOUD_WEBSIDE = "https://powerpanel.cyberpower.com/"

# master page main page switch
PAGE_MONITOR = "monitor"
PAGE_ENERGY = "energy"
PAGE_CONFIG = "config"
PAGE_INFO = "info"

EMQ_HOST = buildConfig.EMQ_HOST  # For EMQ Server
EMQ_PORT = buildConfig.EMQ_PORT
WEBSITE_SERVER_HOST = buildConfig.WEBSITE_SERVER_HOST  # For REST API
WEBSITE_SERVER_PORT = 443

# REST API URL
LOGIN_API_URL = 'https://' + WEBSITE_SERVER_HOST + '/LoginAccountWithDeviceInfo'
LOGOUT_API_URL = 'https://' + WEBSITE_SERVER_HOST + '/Personal/api/Service/LogoutAccount'
UPDATE_DEVICE_INFOR_API_URL = 'https://' + WEBSITE_SERVER_HOST + '/Personal/api/Service/UpdateDeviceInfo'
CHECK_DUPLICATE_DEVICE_NAME_API_URL = 'https://' + WEBSITE_SERVER_HOST + '/Personal/api/Service/CheckDuplicateDeviceNameByAccount'
ADD_DEVICE_LOG_APP_API_URL = 'https://' + WEBSITE_SERVER_HOST + '/status/log/app/add'

MODE = buildConfig.MODE

PPP_DOWNLOAD_URL = 'https://www.cyberpower.com/global/en/product/series/powerpanel%C2%AE_personal#downloads'
# Software update API URL
if BUILD_FOR is BuildConfiguration.Test.value:
    API_BASE_URL = "powerpaneldemoservice"
elif BUILD_FOR is BuildConfiguration.Production.value:
    API_BASE_URL = "powerpanelservice"
SOFTWARE_UPDATE_URL = 'https://' + API_BASE_URL + '.cyberpower.com/ppsoftware/api/update/getFile'