import os, platform, sys, configparser, datetime, traceback
from System import module, settings

if platform.system() == 'Windows':
    import winreg

class setting:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
        return class_._instance

    def __init__(self):

        if not hasattr(self, 'iniPath'):
            self.writeSetting()

    def writeSetting(self):
        if platform.system() == 'Windows':
            try:
                bitness = platform.architecture()[0]
                appDataPath, defaultUser = self.readDefaultSetting()  # 由System/logger.ini讀取第一次安裝PPP之user appDataPath & user name

                if module.Module()._module == module.ModuleEnum.Client:
                    currentAppDataPath, currentUser = self.readRegistry()  # 當下運行PPP Client之user appDataPath & user name
                    if len(defaultUser) > 0 and (currentUser != defaultUser):  # currentUser != defaultUser不寫client log
                        return

                    if len(appDataPath) == 0 and len(defaultUser) == 0:  # System/logger.ini無設定值時
                        appDataPath = currentAppDataPath
                        defaultUser = currentUser

                if len(appDataPath) > 0:
                    if not os.path.isdir(appDataPath):
                        os.makedirs(appDataPath)
                    self.iniPath = appDataPath
                    self.iniUser = defaultUser
                    self.writeDebugMsg("[{0}]: Debug mode start".format(str(datetime.datetime.now())))
                    self.writeDebugMsg(
                        "[{0}]: Windows {1} release no.:{2}".format(str(datetime.datetime.now()), str(bitness),
                                                                    str(platform.release())))
                    self.writeDebugMsg(
                        "[{0}]: Run process {1}".format(str(datetime.datetime.now()), str(module.Module()._module)))
                    self.writeDebugMsg(
                        "[{0}]: APPDATA path:{1}".format(str(datetime.datetime.now()), str(appDataPath)))
                    self.writeDebugMsg(
                        "[{0}]: USERNAME:{1}".format(str(datetime.datetime.now()), str(defaultUser)))
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                # self.writeDebugMsg(traceback.format_exc()) # for local debug
        elif platform.system() == 'Darwin':

            appDataPath, defaultUser = self.readDefaultSetting()
            if module.Module()._module == module.ModuleEnum.Client:
                userhome = os.path.expanduser('~')
                currentAppDataPath = os.path.join(userhome, "Documents", "cpsppp")
                currentUser = os.path.split(userhome)[-1]

                if len(defaultUser) > 0 and (currentUser != defaultUser):  # currentUser != defaultUser不寫client log
                    return

                if len(appDataPath) == 0 and len(defaultUser) == 0:  # System/logger.ini無設定值時
                    appDataPath = currentAppDataPath
                    defaultUser = currentUser

            self.iniPath = appDataPath
            self.iniUser = defaultUser



    def writeDebugMsg(self, msg):
        if self.iniPath is not None and len(self.iniPath) > 0:
            try:
                isConfigExist = os.path.isfile("log.json")
                if isConfigExist:
                    # debugFile = "C:\\Users\\xxx\\AppData\\Roaming\\PowerPanelPersonal\\debug.txt" # for local debug
                    debugFile = os.path.join(self.iniPath, "debug.txt")
                    if not os.path.isfile(debugFile):
                        with open(debugFile, 'w'):  # create a empty file
                            pass

                    with open(debugFile, 'r') as file:
                        contents = file.readlines()

                    index = len(contents) + 1
                    contents.insert(index, (msg + "\n"))

                    with open(debugFile, 'w') as file:
                        contents = "".join(contents)
                        file.write(contents)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)

    def readDefaultSetting(self):

        defaultPath = ""
        defaultUser = ""
        if os.path.isfile(settings.loggerIni):
            cp = configparser.ConfigParser()
            cp.read(settings.loggerIni)
            defaultPath = cp.get('DefaultSetting', 'app_data_path')
            defaultUser = cp.get('DefaultSetting', 'user')
        return defaultPath, defaultUser

    def readRegistry(self):
        appDataPath = ""
        defaultUser = ""
        bitness = platform.architecture()[0]
        if bitness == '32bit':
            other_view_flag = winreg.KEY_WOW64_64KEY
        elif bitness == '64bit':
            other_view_flag = winreg.KEY_WOW64_32KEY

        reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        new_key_value = winreg.OpenKey(reg_connection, r"Volatile Environment",
                                       access=winreg.KEY_READ | other_view_flag)

        key = 0
        while (len(appDataPath) == 0 or len(defaultUser) == 0) and key <= 1000:
            try:
                show_sub_keys = winreg.EnumValue(new_key_value, key)
                if show_sub_keys[0] == "APPDATA":
                    appDataPath = os.path.join(show_sub_keys[1], "PowerPanelPersonal")
                if show_sub_keys[0] == "USERNAME":
                    defaultUser = show_sub_keys[1]
                key += 1
            except Exception:
                break

        return appDataPath, defaultUser

