import os, platform
import RootDir
from pathlib import Path

# PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = RootDir.PROJECT_ROOT_PATH
RESOURCE_PATH = os.path.join(PROJECT_ROOT_PATH, "resources")
STYLESHEET_PATH = os.path.join(RESOURCE_PATH, "stylesheet")
CONTEXT_PATH = os.path.join(RESOURCE_PATH, "context")
I18N_PATH = os.path.join(PROJECT_ROOT_PATH, "i18n")
IMAGE_PATH = os.path.join(RESOURCE_PATH, "images")
DLL_PATH = os.path.join(PROJECT_ROOT_PATH, "bin")
FONT_PATH = os.path.join(RESOURCE_PATH, "fonts")
USER_PATH = os.path.join(RESOURCE_PATH, "user")
ASSETS_PATH = os.path.join(PROJECT_ROOT_PATH, "assets")
DB_ABSOLUTE_PATH = os.path.join(ASSETS_PATH, "PPPE_Db.db")
PPPE_DB = "sqlite:///" + DB_ABSOLUTE_PATH
COUNTRY_TABLE_PATH = os.path.join(PROJECT_ROOT_PATH, "CountryTable.xml")
USER_OS_HOME_DIRECTORY_PATH = str(Path.home())
USER_PPP_FOLDER_PATH = os.path.join(USER_OS_HOME_DIRECTORY_PATH, "PowerPanelPersonal")
CONTEXT_MENU_PATH = os.path.join(I18N_PATH, "contextMenu")
# mac source code python module都會多一層lib資料夾
if platform.system() == 'Windows':
    UTILITY_PATH = os.path.join(PROJECT_ROOT_PATH, "Utility")
    SYSTEM_PATH = os.path.join(PROJECT_ROOT_PATH, "System")
    MODELS_PATH = os.path.join(PROJECT_ROOT_PATH, "model_Json")
elif platform.system() == 'Darwin':
    UTILITY_PATH = os.path.join(PROJECT_ROOT_PATH,"lib", "Utility")
    SYSTEM_PATH = os.path.join(PROJECT_ROOT_PATH,"lib", "System")
    MODELS_PATH = os.path.join(PROJECT_ROOT_PATH,"lib", "model_Json")

# define file path
nativeDll = os.path.join(DLL_PATH, "ppbedrvc.dll")
nativeDllMac = os.path.join(DLL_PATH, "MacOS/libppbedrvc.dylib")
shutdownDll = os.path.join(DLL_PATH, "shutdown.dll")
shutdownMac = os.path.join(DLL_PATH, "MacOS/shutdown.sh")
beepDll = os.path.join(DLL_PATH, "winbeep.dll")
hibernateDll = os.path.join(DLL_PATH, "hibernate.dll")
hibernateMac = os.path.join(DLL_PATH, "MacOS/hibernate.sh")
langSetting = os.path.join(I18N_PATH, "language.txt")
srvSetting = os.path.join(PROJECT_ROOT_PATH, "set_srv.bat")
loggerIni = os.path.join(SYSTEM_PATH, "logger.ini")
week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']  # 與schedule相關
shutdownDuration = 120  # 關機緩衝時間, 避免電腦早於ups關機(sec)

FONT_DEFAULT = "Roboto"
FONT_MS_JP = "MS UI Gothic"
FONT_SIZE_IN_PX = 13

# Secrets
PWD_KEY = "cyberpower@TP08!"
EMQ_ACC = "cps_user"
EMQ_PWD = "9cccd1b06bb1ed62179c9388fb27784d2badb297"

EVENT_LOG_LIMIT = 1000
