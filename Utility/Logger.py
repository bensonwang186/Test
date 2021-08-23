import os, platform
import logging
import sys
import traceback
import json

from System import settings, module, loggerSetting
from logging.config import dictConfig
class LogIns:

    _instance = None
    _logger = None
    _is_client_connected = False # 給daemon用來判斷是否要停止讀取config檔是否存在的旗標

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'console': {
                'format': '[%(asctime)s][%(levelname)s] %(name)s '
                          '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
                'datefmt': '%H:%M:%S',
            }
        },

        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            }
        },

        'loggers': {
            'ppp': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'your_app_ppp': {
                'level': 'DEBUG',
                'propagate': True,
            }
        }
    }

    @property
    def logger(self):
        if self._logger == None:
            print("self._logger == None: {}".format(self._logger))
            return self.getLoggerSentry()
        print("logger is not None: {}".format(self._logger))
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger

    @property
    def is_client_connected(self):
        return self._is_client_connected

    @is_client_connected.setter
    def is_client_connected(self, is_client_connected):
        self._is_client_connected = is_client_connected

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
            class_._instance._initialized = False
        return class_._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    def getLoggerSentry(self):
        # for daemon check
        if module.Module()._module == module.ModuleEnum.Deamon and self.is_client_connected:
            if self._logger != None:
                return self._logger
            else: # 判斷要從Logging或log.json取得logger
                self._logger = self.decide_logger()
                return self._logger
        elif module.Module()._module == module.ModuleEnum.Deamon and not self.is_client_connected: # client連上前都直接回傳logging，client未連上時會先暫時傳LOGGING的logger
            dictConfig(self.LOGGING)
            return logging.getLogger('PPP')

        elif module.Module()._module == module.ModuleEnum.Client:
            if self._logger != None:
                return self._logger
            else: # 判斷要從Logging或log.json取得logger
                self._logger = self.decide_logger()
                return self._logger

    def decide_logger(self):
        try:

            if platform.system() == 'Windows':
                isConfigExist = os.path.isfile("log.json")
            elif platform.system() == 'Darwin':
                log_file = settings.os.path.join(settings.PROJECT_ROOT_PATH, "..", "..", "..", "log.json")
                isConfigExist = os.path.isfile(log_file)

            self.loggerSetting = loggerSetting.setting()

            if isConfigExist:
                # self.writeDebugMsg("{0} : log.json IS EXIST".format(str(now)))
                if platform.system() == 'Windows':

                    if hasattr(self.loggerSetting, 'iniPath'):
                        appdatapath = self.loggerSetting.iniPath

                        if not isinstance(appdatapath, str) or len(appdatapath) == 0:
                            dictConfig(self.LOGGING)
                        else:  # logging path exist
                            if not os.path.isdir(appdatapath):
                                os.makedirs(appdatapath)

                            with open('log.json') as f:
                                config_dict = json.load(f)
                                for key, handler in config_dict["handlers"].items():
                                    if "filename" in handler:
                                        handler["filename"] = os.path.join(appdatapath, handler["filename"])
                                dictConfig(config_dict)
                    else:
                        dictConfig(self.LOGGING)

                elif platform.system() == 'Darwin':
                    if hasattr(self.loggerSetting, 'iniPath'):
                        appdatapath = self.loggerSetting.iniPath
                        # (not os.path.isdir(appdatapath) and module.Module()._module == module.ModuleEnum.Deamon) : 如果是daemon且log的目錄還沒創出則先讀LOGGING
                        # if not isinstance(appdatapath, str) or len(appdatapath) == 0 or (not os.path.isdir(appdatapath) and module.Module()._module == module.ModuleEnum.Deamon):
                        if not isinstance(appdatapath, str) or len(appdatapath) == 0:
                            dictConfig(self.LOGGING)
                            return logging.getLogger('PPP')
                        else:  # logging path exist
                            if not os.path.isdir(appdatapath):
                                if module.Module()._module == module.ModuleEnum.Client:
                                    os.makedirs(appdatapath)
                            with open(log_file) as f:
                                config_dict = json.load(f)
                                self.reorganize_config(config_dict, appdatapath)
                                dictConfig(config_dict)
                    else:
                        dictConfig(self.LOGGING)
                        return logging.getLogger('PPP')
            else:
                dictConfig(self.LOGGING)
                return logging.getLogger('PPP')
            if module.Module()._module == module.ModuleEnum.Client:
                return logging.getLogger('client')
            else:
                return logging.getLogger('daemon')

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(e)


    def reorganize_config(self, config_dict, appdatapath):
        if module.Module()._module == module.ModuleEnum.Client:
            if module.Module()._module == module.ModuleEnum.Client:
                daemon_dict = config_dict['loggers'].pop('daemon')
                for h in daemon_dict['handlers']:
                    if h != "console":
                        config_dict['handlers'].pop(h)
        elif module.Module()._module == module.ModuleEnum.Deamon:
            daemon_dict = config_dict['loggers'].pop('client')
            for h in daemon_dict['handlers']:
                if h != "console":
                    config_dict['handlers'].pop(h)
        for key, handler in config_dict["handlers"].items():
            if "filename" in handler:
                handler["filename"] = os.path.join(appdatapath, handler["filename"])

    # for debug
    def getMobileLogger(self):
        log_format = '[%(asctime)s][%(levelname)s] %(name)s ''%(filename)s:%(funcName)s:%(lineno)d | %(message)s'
        log_file_path = os.path.join(settings.USER_OS_HOME_DIRECTORY_PATH, "pppm_info.txt")

        logger = logging.getLogger('pppmLoger')
        hdlr = logging.FileHandler(log_file_path)
        formatter = logging.Formatter(log_format)
        hdlr.setFormatter(formatter)

        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        return logger


