import datetime
import logging
import sys
import traceback
import socket
from datetime import date
from System import settings
from enum import Enum
from bitstring import BitArray
import os
import subprocess
from Utility import Logger
import platform
import hashlib
import hmac

CREATE_NO_WINDOW = 0x08000000  # hide console
def stringParse2Float(inputStr):
    try:
        if inputStr is not None:
            result = float(inputStr) / 1000
        else:
            result = ""
    except ValueError:
        result = ""
        Logger.LogIns().logger.info("System Function error: StringParse2Float")

    return result


def stringParse2Min(inputStr):
    try:
        if inputStr is not None:
            result = float(inputStr) / 60
        else:
            result = ""
    except ValueError:
        result = ""
        Logger.LogIns().logger.info("System Function error: StringParse2Min")

    return result


def floatTryParse(value):
    try:
        float(value)
        return True
    except ValueError:
        Logger.LogIns().logger.info("System Function error: isFloat")
        return False


def intTryParse(value):
    try:
        int(value)
        return True
    except ValueError:
        Logger.LogIns().logger.info("System Function error: intTryParse")
        return False

def intParse(value):
    if intTryParse(value):
        return int(value)
    else:
        return 0

def stringIsNullorEmpty(inputStr):
    if inputStr is None or not inputStr:
        return True
    else:
        return False


def getCurrentWeek():
    today = getDatetimeNonw()
    dates = [today + datetime.timedelta(days=i) for i in range(0 - today.isoweekday(), 7 - today.isoweekday())]

    return dates  # week means Sun to Sat


def getNext7Weekdays():
    today = getDatetimeNonw()
    dic = dict()
    for index, val in enumerate(settings.week):
        if index == today.weekday():
            dic[val] = today.replace(hour=00, minute=00, second=00, microsecond=00)
        else:
            dic[val] = nextWeekday(today, index).replace(hour=00, minute=00, second=00, microsecond=00)

    return dic


def nextWeekday(day, weekday):
    days_ahead = weekday - day.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return day + datetime.timedelta(days_ahead)


def nextWeekDayTime(daytime):
    now = datetime.datetime.now()
    if daytime <= now:  # Target day already happened this week
        daytime += datetime.timedelta(7)
    return daytime


def delayOnTime(onTime, offTime):
    while onTime <= offTime:
        onTime += datetime.timedelta(7)
    return onTime


def formatTime(x):
    days, remainder = divmod(x, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = ""
    if days > 0:
        result += str(days) + " days, "

    if hours > 0:
        result += str(hours) + " hours, "

    if minutes > 0:
        result += str(minutes) + " mins, "

    if seconds > 0:
        result += str(seconds) + " secs"

    return result


def datetimeHandler(x):
    if isinstance(x, (datetime.datetime, date)):
        try:
            xd = x.isoformat().replace("T", " ")
            return xd
        except Exception:
            traceback.print_exc(file=sys.stdout)
    raise TypeError("Unknown type")


def datetimeParser(dct):
    format = "%Y-%m-%d %H:%M:%S"
    for k, v in dct.items():
        if k == "startDate" or k == "endDate":
            try:
                dct[k] = datetime.strptime(v, format)
            except:
                traceback.print_exc(file=sys.stdout)
    return dct


def getDatetimeNonw():
    return datetime.datetime.now().replace(microsecond=0)


def transferStringToDatetime(string):
    format = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(string, format)


def jsonSerialize(x):
    return x.toJson()


def internet_connected(host, port):
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        traceback.print_exc(file=sys.stdout)

    return False


def getSMBiosUUID():
    # platform.system() -> Windows, Linux, Darwin
    print("os: "+str(os.name))
    print(sys.platform)
    if platform.system() == 'Windows':
        try:
            SMBiosUUID = subprocess.check_output("wmic path win32_computersystemproduct get uuid",
                                    creationflags=CREATE_NO_WINDOW).decode("ascii", "ignore") \
                .replace("\r", "").replace("\n", "").replace("UUID", "").replace(" ", "")

            Logger.LogIns().logger.info("***altsn-chk device.SMBiosUUID on Windows: " + str(SMBiosUUID) + "***")
            return SMBiosUUID
        except Exception:
            Logger.LogIns().logger.info("***fetch SMBiosUUID on Windows failed***")
            return ""
    elif platform.system() == 'Darwin':
        import re
        machine_uuid_str = ''

        p = os.popen('ioreg -rd1 -c IOPlatformExpertDevice | grep -E \'(UUID)\'', "r")

        while 1:
            line = p.readline()
            if not line: break
            machine_uuid_str += line

        match_obj = re.compile('[A-Z,0-9]{8,8}-' + \
                               '[A-Z,0-9]{4,4}-' + \
                               '[A-Z,0-9]{4,4}-' + \
                               '[A-Z,0-9]{4,4}-' + \
                               '[A-Z,0-9]{12,12}')

        results = match_obj.findall(machine_uuid_str)
        if len(results) > 0:
            SMBiosUUID = results[0]
            Logger.LogIns().logger.info("***altsn-chk device.SMBiosUUID on mac: " + str(SMBiosUUID) + "***")
            return SMBiosUUID
        else:
            Logger.LogIns().logger.info("***fetch SMBiosUUID on mac failed***")
            return ""


def getProcessorId():
    if platform.system() == 'Windows':
        try:
            processorId = subprocess.check_output("wmic path win32_processor get processorid",
                                    creationflags=CREATE_NO_WINDOW).decode("ascii",
                                                                           "ignore") \
                .replace("\r", "").replace("\n", "").replace("ProcessorId", "").replace(" ", "")
            Logger.LogIns().logger.info("***altsn-chk device.ProcessorId: " + str(processorId) + "***")
            return processorId
        except Exception:
            Logger.LogIns().logger.info("***fetch processor id failed***")

    elif platform.system() == 'Darwin':
        Logger.LogIns().logger.info("***fetch processor id on mac, it will be empty***")
        return ""

def listToEnum(member_list, enum_name, enum_start):
    member_str = ""
    for i,val in enumerate(member_list):
        member_str += val.replace(" ", "_")
        if (i+1) < len(member_list):
            member_str += ","

    return Enum(enum_name, member_str, start=enum_start)

def hexStringToBoolArray(hex_string):
    b = BitArray(hex=hex_string)  # hex string to BitArray
    return [x == '1' for x in list(b.bin)]  #　split a binary string into array of characters -> run for loop

def md5Hash(msg):

    if not isinstance(msg, str) or stringIsNullorEmpty(msg):
        return None

    result = hashlib.md5(msg.encode()).hexdigest()
    return result

def sha512Hash(key, msg):

    if not isinstance(key, str) or stringIsNullorEmpty(key):
        return None

    if not isinstance(msg, str) or stringIsNullorEmpty(msg):
        return None

    result = hmac.new(bytes(key, encoding="utf8"), msg.encode('utf8'), digestmod=hashlib.sha512).hexdigest()
    return result

