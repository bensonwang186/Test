
from Events import Event



class Events(object):

    def __init__(self):
        self.eventLists = dict()
        self.buildEvents()


    def buildEvents(self):
        event = Event.Event()
        event.eventId = Event.EventID.ID_UTILITY_FAILURE.value
        event.restoreEventId = Event.EventID.ID_UTILITY_FAILURE_RESTORE.value

        self.eventLists[event.eventId] = event

        event = Event.Event()
        event.eventId = Event.EventID.ID_UTILITY_TRANSFER_HIGH.value
        event.restoreEventId = Event.EventID.ID_UTILITY_FAILURE_RESTORE.value

        self.eventLists[event.eventId] = event

        event = Event.Event()
        event.eventId = Event.EventID.ID_COMMUNICATION_LOST.value
        event.restoreEventId = Event.EventID.ID_UTILITY_FAILURE_RESTORE.value

        self.eventLists[event.eventId] = event

        event = Event.Event()
        event.eventId = Event.EventID.ID_COMMUNICATION_LOST.value
        event.restoreEventId = Event.EventID.ID_COMMUNICATION_ESTABLISHED.value

        self.eventLists[event.eventId] = event

        print(self.eventLists[Event.EventID.ID_UTILITY_FAILURE.value].eventId)
        print(self.eventLists[Event.EventID.ID_UTILITY_FAILURE.value].restoreEventId)
        print(self.eventLists[Event.EventID.ID_COMMUNICATION_LOST.value].eventId)
        print(self.eventLists[Event.EventID.ID_COMMUNICATION_LOST.value].restoreEventId)



