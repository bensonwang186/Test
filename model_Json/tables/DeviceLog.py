import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DeviceLog(Base):
    __tablename__ = 'DeviceLog'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    dsn = Column(TEXT)
    LocalTime = Column(DATETIME, nullable=False)
    ts = Column(INTEGER, nullable=False)  # timestamp
    dcode = Column(INTEGER, nullable=True)
    InSta = Column(INTEGER, nullable=True)
    InVolt = Column(FLOAT, nullable=True)
    InFreq = Column(FLOAT, nullable=True)
    OutSta = Column(INTEGER, nullable=True)
    OutVolt = Column(FLOAT, nullable=True)
    OutFreq = Column(FLOAT, nullable=True)
    OutCur = Column(FLOAT, nullable=True)
    BatSta = Column(INTEGER, nullable=True)
    BatCap = Column(FLOAT, nullable=True)
    BatRun = Column(FLOAT, nullable=True)
    BatVolt = Column(FLOAT, nullable=True)
    BatWar = Column(INTEGER, nullable=True)
    SysSta = Column(TEXT, nullable=True)
    SysTemp = Column(FLOAT, nullable=True)
    EnvTemp = Column(FLOAT, nullable=True)
    EnvHumi = Column(FLOAT, nullable=True)
    SN = Column(TEXT, nullable=True)
    rFV = Column(TEXT, nullable=True)
    rSN = Column(TEXT, nullable=True)
    ReDate = Column(TEXT, nullable=True)
    LP = Column(INTEGER, nullable=True)
    Model = Column(TEXT, nullable=True)
    FV = Column(TEXT, nullable=True)
    RatPow = Column(INTEGER, nullable=True)
    VoltRat = Column(INTEGER, nullable=True)
    WorFreq = Column(TEXT, nullable=True)
    upsState = Column(INTEGER, nullable=True)
    Type = Column(INTEGER, nullable=True)
    Event = Column(TEXT, nullable=True)
    NclOut = Column(TEXT, nullable=True)
    DevOut = Column(INTEGER, nullable=True)
    PowSour = Column(INTEGER, nullable=True)
    Dev = Column(INTEGER, nullable=True)
    DevLoad = Column(FLOAT, nullable=True)
    BatVoltRat = Column(INTEGER, nullable=True)
    lFV = Column(TEXT, nullable=True)
    uFV = Column(TEXT, nullable=True)
    ExtData = Column(TEXT, nullable=True)

    def __init__(self, jsonString=None):
        self.dsn = None
        self.LocalTime = None
        self.ts = None
        self.dcode = None
        self.InSta = None
        self.InVolt = None
        self.InFreq = None
        self.OutSta = None
        self.OutVolt = None
        self.OutFreq = None
        self.OutCur = None
        self.BatSta = None
        self.BatCap = None
        self.BatRun = None
        self.BatVolt = None
        self.BatWar = None
        self.SysSta = None
        self.SysTemp = None
        self.EnvTemp = None
        self.EnvHumi = None
        self.SN = None
        self.rFV = None
        self.rSN = None
        self.ReDate = None
        self.LP = None
        self.Model = None
        self.FV = None
        self.RatPow = None
        self.VoltRat = None
        self.WorFreq = None
        self.upsState = None
        self.Type = None
        self.Event = None
        self.NclOut = None
        self.DevOut = None
        self.PowSour = None
        self.Dev = None
        self.DevLoad = None
        self.BatVoltRat = None
        self.lFV = None
        self.uFV = None
        self.ExtData = None

        # if jsonString:
        #     self.__dict__ = json.loads(jsonString, object_hook = self.datetime_parser)

    def __repr__(self):  # control what this function returns for its instances.

        d = self.objectAsDict(self)
        try:
            jsonString = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return jsonString

    def datetime_parser(self, dct):
        format = "%Y-%m-%d %H:%M:%S"
        for k, v in dct.items():
            if k == "LocalTime":
                try:
                    if v is not None:
                        dct[k] = datetime.strptime(v, format)
                except:
                    traceback.print_exc(file=sys.stdout)
        return dct

    def datetime_handler(self, x):
        if isinstance(x, datetime):
            return x.isoformat().replace("T", " ")
        raise TypeError("Unknown type")

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return dic

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            jsonString = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return jsonString

# a= DeviceLog()
# print(a)