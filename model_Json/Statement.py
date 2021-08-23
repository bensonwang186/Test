class Statement:
    def __init__(self, id=-1, params=list()):  # id=-1: define a default value if one is not passed
        self.Id = id  # value id
        self.params = list()  # value paramenter
        self.errCode = -1  # statement error code

        for i in range(len(params)):
            self.params.append(params[i])

        self.results = list()
        self.references = list()

    '''__str__ print statement to compute the "informal" string representation of an object.'''

    def __str__(self):
        return str(self.__dict__)  # __dict__: A dictionary or other mapping object used to store an object’s (
        # writable) attributes.

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def hasParams(self):
        if (self.params is None) or (not self.params):
            return False
        else:
            return True

    @property
    def hasResults(self):
        if not (self.results is None) and len(self.results) != 0:  # results != null && ! results.isEmpty()
            return True
        else:
            return False

    def setId(self, id):
        self.Id = id

    def setErrCode(self, errCode):
        self.errCode = errCode

    class Error:
        DRVERR_SUCCESS = 0
        DRVERR_CMDID_INVALID = 1
        DRVERR_CMD_NOT_SUPPORT = 2
        DRVERR_DEVID_INVALID = 3
        DRVERR_DEVICE_WRONG = 4
