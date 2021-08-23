from enum import Enum, auto

class Event(object):

    def __init__(self):
        self._id = None
        self._restoreEventId = None

    @property
    def eventId(self):
        return self._id

    @eventId.setter
    def eventId(self, value):
        self._id = value

    @property
    def restoreEventId(self):
        return self._restoreEventId

    @restoreEventId.setter
    def restoreEventId(self, value):
        self._restoreEventId = value

class EventID(Enum):
    # ID_UTILITY_FAILURE = 0
    # ID_UTILITY_FAILURE_RESTORE = 1
    # ID_COMMUNICATION_LOST = 2
    # ID_COMMUNICATION_ESTABLISHED = 3
    # ID_UTILITY_TRANSFER_HIGH = 4
    # ID_UTILITY_TRANSFER_HIGH_RESTORE = 5
    # ID_UTILITY_TRANSFER_LOW = 6
    # ID_UTILITY_TRANSFER_LOW_RESTORE = 7
    # ID_AVR_BOOST_ACTIVE = 8
    # ID_AVR_BOOST_RESTORE = 9
    # ID_AVR_BUCK_ACTIVE = 10
    # ID_AVR_BUCK_RESTORE = 11

    ID_UTILITY_FAILURE = 0
    ID_UTILITY_FAILURE_RESTORE = 1
    ID_AVR_BOOST_ACTIVE = 2
    ID_AVR_BUCK_ACTIVE = 3
    ID_AVR_BOOST_RESTORE = 4
    ID_AVR_BUCK_RESTORE = 5
    ID_UTILITY_TRANSFER_HIGH = 6
    ID_UTILITY_TRANSFER_HIGH_RESTORE = 7
    ID_UTILITY_TRANSFER_LOW = 8
    ID_UTILITY_TRANSFER_LOW_RESTORE = 9
    ID_COMMUNICATION_LOST = 80
    ID_COMMUNICATION_ESTABLISHED = 81





