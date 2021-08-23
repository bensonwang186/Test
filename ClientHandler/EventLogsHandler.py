import sys, json, traceback
from major import Command
from System import systemFunction
from Utility import Logger

class EventLogsHandler(object):
    def __init__(self, eventLogsPage, client, device, tray):
        self.eventLogsPage = eventLogsPage
        self.client = client
        self.tray = tray

        # connect page signal for settings
        self.eventLogsPage.setEventFilterSignal.connect(self.askEventsDisplay)

        # connect summary data signal for update
        self.client.updateEventLogPageSignal.connect(self.updateEventsDisplay)

        self.eventLogsPage.clearEventLogsSignal.connect(self.clearEventLogs)
        self.client.updateClearEventLogsSignal.connect(self.clearEventLogsDisplay)


    def askEventsDisplay(self, tupleData):
        Logger.LogIns().logger.info("askEventsDisplay")
        try:
            if not self.tray.initFlag:
                data = dict()
                data["startDate"] = tupleData[0]
                data["endDate"] = tupleData[1]

                if tupleData[2] is not None:
                    data["level"] = tupleData[2]
                if tupleData[3] is not None:
                    data["queryStr"] = tupleData[3]
                if tupleData[4] is not None:
                    data["limit"] = tupleData[4]
                if tupleData[5] is not None:
                    data["paging"] = tupleData[5]
                if tupleData[6] is not None:
                    data["currentPageNo"] = tupleData[6]
                if tupleData[7] is not None:
                    data["limitId"] = tupleData[7]

                try:
                    jsonData = json.dumps(data, default=systemFunction.datetimeHandler)
                except Exception:
                    Logger.LogIns().logger.error(traceback.format_exc())
                    Logger.LogIns().logger.error(jsonData)

                self.client.queryRequest(Command.TARGET_EVENT_LOG_PAGE, jsonData)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def updateEventsDisplay(self, data):

        Logger.LogIns().logger.info("updateEventsDisplay")
        try:
            logs = []
            pageIndex = dict()
            if data is not None and data != "[]":
                tempList = json.loads(data)

                if len(tempList) == 2:
                    temp = tempList[0]
                    pageIndex = tempList[1]
                    for i,item in enumerate(temp):
                        logs.append(json.loads(item))

            self.eventLogsPage.updatePage(logs, pageIndex)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def clearEventLogs(self):

        Logger.LogIns().logger.info("clearEventLogs")
        try:
            self.client.queryRequest(Command.TARGET_CLEAR_ALL_EVENTLOGS)
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def clearEventLogsDisplay(self, flag):

        Logger.LogIns().logger.info("clearEventLogsDisplay")
        try:
            if flag:
                self.updateEventsDisplay(None)  # update table
            else:
                Logger.LogIns().logger.error("Clear event logs failed.")

            # self.eventLogsPage.confirmDialog.accept()
        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
        finally:
            self.eventLogsPage.confirmDialog.accept()


