#!/usr/bin/env python

import traceback
from Utility import Logger

import platform
import threading
from ctypes import cdll, c_char_p, c_bool, create_string_buffer

from System import settings, systemDefine


class DriverTransaction(systemDefine.Singleton):
    ppbe = None
    _lock = None
    def __init__(self):
        if self.ppbe is None:
            if platform.system() == 'Windows':
                self.ppbe = cdll.LoadLibrary(settings.nativeDll)
            elif platform.system() == 'Darwin':
                self.ppbe = cdll.LoadLibrary(settings.nativeDllMac)
            # elif platform.system() == 'Linux':

        if self._lock is None:
            self._lock = threading.Lock()

    def request(self, cmdStr):
        try:
            Logger.LogIns().logger.error("******DriverTransaction request START******")
            Logger.LogIns().logger.error("DriverTransaction cmdStr: " + str(cmdStr))
            cmd = cmdStr.encode('utf-8')
            Logger.LogIns().logger.error("DriverTransaction cmd: " + str(cmd))
            # self.ppbe.request.restype = c_char_p
            self.ppbe.request.restype = c_bool
            Logger.LogIns().logger.error("DriverTransaction SET REQUEST TYPE")
            #response = self.ppbe.request(cmd)  # return bytes
            
            response = create_string_buffer(4096)
            responseFlag = self.ppbe.request(cmd, response)  # return bytes
            Logger.LogIns().logger.error("DriverTransaction PRINT RESPONSE FLAG: " + str(responseFlag))

            Logger.LogIns().logger.error("DriverTransaction GET RESPONSE")
            Logger.LogIns().logger.error("DriverTransaction PRINT RESPONSE BYTES: " + str(response))

            # io.BytesIO(response)  # In-memory binary streams are also available as BytesIO objects
            # respStr = response.decode("utf-8", errors='ignore')  # bytes convert to string
            respStr = response.value.decode("utf-8", errors='ignore')  # bytes convert to string
            Logger.LogIns().logger.error("DriverTransaction PRINT RESPONSE STRING: " + str(respStr))
            Logger.LogIns().logger.error("******DriverTransaction request END******")
            return respStr
        except Exception:
            Logger.LogIns().logger.error("******DriverTransaction request CATCH ERROR******")
            Logger.LogIns().logger.error(traceback.format_exc())

    def start(self):
        flag = self.ppbe.start()
        return flag

    def stop(self):
        flag = self.ppbe.stop()
        return flag

    def deviceChanged(self, eventType, ptr, name):
        nameS = name.encode('utf-8')
        self.ppbe.deviceChanged(eventType, ptr, nameS)
