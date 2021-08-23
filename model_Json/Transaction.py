import model_Json.DeviceStatusData


class Transaction:
    def __init__(self):
        self.deviceId = -1
        self.state = model_Json.DeviceStatusData.DeviceState.PROXY_STATE_NORMAL  # 0: OK, 1: Device Not Valid
        self.statements = list()
        self.statementsDic = dict()

    '''__str__ print statement to compute the "informal" string representation of an object.'''

    def __str__(self):
        return str(self.__dict__)  # __dict__: A dictionary or other mapping object used to store an object’s (
        # writable) attributes.

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def setDeviceId(self, deviceId):
        self.deviceId = deviceId

    def add(self, stat):
        self.statements.append(stat)

    def setState(self, state):
        self.state = state
