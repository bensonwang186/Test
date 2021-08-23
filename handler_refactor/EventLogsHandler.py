import sys, traceback, json
from System import systemFunction
from major import Command

class EventLogsHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.device.dataSource.updateEventLogsPageSignal.connect(self.updateEventLogsSlot)

    def updateEventLogsSlot(self, filter):
        try:
            if filter is not None:
                startDate = filter[0]
                endDate = filter[1]
                level = filter[2]
                queryStr = filter[3]
                limit = filter[4]
                paging = filter[5]

                if len(filter) >= 8:
                    currentPageNo = filter[6]
                    limitId = filter[7]

                logs, pageIndex = self.device.dataSource.queryEventLog(startDate, endDate, level, queryStr, limit, paging, currentPageNo, limitId)
            else:
                now = systemFunction.getDatetimeNonw()
                logs, pageIndex = self.device.dataSource.queryEventLog(now, now, None, None, 10, False, None, None)

            jsonlogs = [item.toJson() for item in logs]
            tup = (jsonlogs, pageIndex)
            jsonData = json.dumps(tup)
            self.server.sendDataToClients(Command.TARGET_EVENT_LOG_PAGE, jsonData)

        except Exception:
            traceback.print_exc(file=sys.stdout)


