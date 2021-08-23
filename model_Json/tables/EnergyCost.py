import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect, ForeignKey
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import FLOAT
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class EnergyCost(Base):
    __tablename__ = 'EnergyCost'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    startTime = Column(DATETIME, nullable=True)
    endTime = Column(DATETIME, nullable=True)
    cost = Column(FLOAT, nullable=True)
    energySettingId = Column(INTEGER, ForeignKey('EnergySetting.id'))
    updateTime = Column(DATETIME, nullable=True)
    energySetting = relationship('EnergySetting', back_populates='energyCost')  # 建立雙向關聯, 注意back_populates屬性

    def __init__(self, jsonString=None):
        self.startTime = None
        self.endTime = None
        self.cost = None
        self.energySettingId = None
        self.updateTime = None

        if jsonString:
            self.__dict__ = json.loads(jsonString, object_hook=self.datetime_parser)

    def __repr__(self):
        return "EnergyCost('{}','{}', '{}')".format(
            self.startTime,
            self.endTime,
            self.cost,
            self.energySettingId,
            self.updateTime
        )


    def datetime_parser(self, dct):
        format = "%Y-%m-%d %H:%M:%S"
        for k, v in dct.items():
            if "Time" in k or "time" in k:
                try:
                    dct[k] = datetime.strptime(v, format)
                except:
                    pass
        return dct


    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        for subObj in dic.values():
            if isinstance(subObj, (datetime, date)):
                subObj = subObj.isoformat().replace("T", " ")
        return dic

    def datetime_handler(self, x):
        if isinstance(x, datetime):
            x = x.replace(microsecond=0)
            return x.isoformat().replace("T", " ")
        raise TypeError("Unknown type")

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr

class EnergySetting(Base):
    __tablename__ = 'EnergySetting'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    country = Column(TEXT, nullable=True)
    co2EmittedKg = Column(FLOAT, nullable=True)
    co2EmittedLb = Column(FLOAT, nullable=True)
    measurement = Column(INTEGER, nullable=True)
    updateTime = Column(DATETIME, nullable=True)
    energyCost = relationship("EnergyCost", back_populates="energySetting")  # 建立雙向關聯

    def __init__(self, jsonString=None):
        self.country = None
        self.co2EmittedKg = None
        self.co2EmittedLb = None
        self.measurement = None
        self.updateTime = None
        if jsonString:
            try:
                self.__dict__ = json.loads(jsonString)
            except Exception:
                traceback.print_exc(file=sys.stdout)

    def __repr__(self):
        return "EnergySetting('{}','{}', '{}')".format(
            self.country,
            self.co2EmittedKg,
            self.co2EmittedLb,
            self.measurement,
            self.updateTime
        )

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        for subObj in dic.values():
            if isinstance(subObj, (datetime, date)):
                subObj = subObj.isoformat().replace("T", " ")
        return dic

    def datetime_handler(self, x):
        if isinstance(x, datetime):
            x = x.replace(microsecond=0)
            return x.isoformat().replace("T", " ")
        raise TypeError("Unknown type")

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr