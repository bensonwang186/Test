import json
from System import systemFunction
from major import Command

class SummaryHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.device.dataSource.updateEventLogSignal.connect(self.updateSummaryEventsSlot)

    def updateSummaryEventsSlot(self):
        data = self.device.dataSource.queryEventLogByDuration(self.device.summaryFilter)
        jsonData = json.dumps(data, ensure_ascii=False, default=systemFunction.jsonSerialize)
        self.server.sendDataToClients(Command.TARGET_EVENT_LOG, jsonData)


