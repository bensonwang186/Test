
import json
import hashlib
import datetime
from sqlalchemy import inspect
class Verifier:

    # key = None
    data = None
    sha1 = None


    def __init__(self, jsonString = None):
        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def verify(self, data, encodeData):
        if isinstance(data, str):
            data = bytes(data, "utf-8")
        m = hashlib.sha1(b"cyber")
        m.update(data)
        mysideEncode = m.hexdigest()
        if encodeData == mysideEncode:
            return True
        return False

    def genEncode(self):
        m = hashlib.sha1(b"cyber")
        self.data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bData = bytes(self.data, "utf-8")
        m.update(bData)
        self.sha1 = m.hexdigest()
        return self.sha1

    def toJson(self):

        return json.dumps(self.__dict__)