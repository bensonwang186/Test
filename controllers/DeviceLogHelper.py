import sys
import traceback
import json
from model_Json.tables.DeviceLog import DeviceLog

class DevLogHelper(object):
    def __init__(self, device):
        self.device = device

    def saveLogs(self, fetchData, currentEvents, currentEventStatData):
        data = DeviceLog()
        data.dsn = fetchData.SN
        data.dcode = self.device.dcode
        data.Type = fetchData.Type
        data.Dev = fetchData.Dev

        if len(currentEvents) > 0:
            data.Event = str(currentEvents).strip('[]')

        data.PowSour = fetchData.PowSour
        data.BatCap = fetchData.BatCap
        data.BatRun = fetchData.BatRun
        data.OutVolt = fetchData.OutVolt
        data.Load = fetchData.Load
        data.InSta = fetchData.InSta
        data.OutSta = fetchData.OutSta
        data.BatSta = fetchData.BatSta
        data.Model = fetchData.Model
        data.FV = fetchData.FV
        data.LP = fetchData.LP
        data.RatPow = fetchData.RatPow
        data.Out = fetchData.Out
        data.NclOut = fetchData.NclOut
        data.SN = fetchData.SN
        data.upsState = fetchData.upsState

        if len(currentEventStatData) > 0:
            data.ExtData = str(currentEventStatData).strip('[]')

        result = self.device.dataSource.addDeviceLog(data)  # save device_log to DB

        return result