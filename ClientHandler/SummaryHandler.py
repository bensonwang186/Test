import sys
import traceback

from Events.Event import EventID
from major import Command
from Utility import Logger
class SummaryHandler(object):
    def __init__(self, summaryPage, client, device, tray):
        self.summaryPage = summaryPage
        self.client = client
        self.tray = tray

        # connect page signal for settings
        self.summaryPage.setSummaryFilterSignal.connect(self.askSummaryEventsDisplay)

        # connect summary data signal for update
        self.client.updateEventLogSignal.connect(self.updateSummaryEventsDisplay)

    def askSummaryEventsDisplay(self, week):
        if not self.tray.initFlag:
            self.client.queryRequest(Command.TARGET_EVENT_LOG, week)

    def updateSummaryEventsDisplay(self, data):
        from model_Json.tables import EventLog
        import json
        logs = json.loads(data)
        eventDispalyArr = []
        powerProblemTotalNumber = 0
        powerProblemTotalAmount = 0
        voltageRegTotalNumber = 0
        voltageRegTotalAmount = 0
        if len(logs) > 0:
            for item in logs[0]:
                eventDispaly = self.summaryPage.EventDispaly()
                eventDispaly.powerProblem = item[0]
                eventDispaly.numberOfTimes = item[1]
                eventDispaly.amountOfTime = item[2]

                if item[0] == EventID.ID_UTILITY_FAILURE.value or item[0] == EventID.ID_UTILITY_TRANSFER_LOW.value or item[0] == EventID.ID_UTILITY_TRANSFER_HIGH.value:
                    if item[1] is not None:
                        powerProblemTotalNumber += item[1]
                    if item[2] is not None:
                        powerProblemTotalAmount += item[2]

                if item[0] == EventID.ID_AVR_BOOST_ACTIVE.value or item[0] == EventID.ID_AVR_BUCK_ACTIVE.value:
                    if item[1] is not None:
                        voltageRegTotalNumber += item[1]
                    if item[2] is not None:
                        voltageRegTotalAmount += item[2]

                eventDispalyArr.append(eventDispaly)

        powerProblem_TotalDispaly = self.summaryPage.EventDispaly()
        powerProblem_TotalDispaly.powerProblem = "InvertTotal"
        powerProblem_TotalDispaly.numberOfTimes = powerProblemTotalNumber
        powerProblem_TotalDispaly.amountOfTime = powerProblemTotalAmount
        eventDispalyArr.append(powerProblem_TotalDispaly)

        voltageReg_TotalDispaly = self.summaryPage.EventDispaly()
        voltageReg_TotalDispaly.powerProblem = "RegularTotal"
        voltageReg_TotalDispaly.numberOfTimes = voltageRegTotalNumber
        voltageReg_TotalDispaly.amountOfTime = voltageRegTotalAmount
        eventDispalyArr.append(voltageReg_TotalDispaly)
        try:
            # self.summaryPage.updateSummaryPage((eventDispalyArr, EventLog.EventLog(None, None, None, logs[1])))
            # self.summaryPage.renderText()

            eventLog = EventLog.EventLog(logs[1])
            self.summaryPage.updateSummaryPage((eventDispalyArr, eventLog))

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())
