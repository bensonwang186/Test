import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import BOOLEAN
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Schedule(Base):
    __tablename__ = 'Schedule'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    days = Column(TEXT, nullable=True)
    onTime = Column(DATETIME, nullable=True)
    onAction = Column(BOOLEAN, nullable=True)
    offTime = Column(DATETIME, nullable=True)
    offAction = Column(BOOLEAN, nullable=True)
    noneReset = Column(BOOLEAN, nullable=True)
    updateTime = Column(DATETIME, nullable=True)

    def __init__(self, jsonString=None):
        self.days = None
        self.onTime = None
        self.onAction = None
        self.offTime = None
        self.offAction = None
        self.noneReset = None
        self.updateTime = None

        if jsonString:
            self.__dict__ = json.loads(jsonString, object_hook=self.datetime_parser)

    def __repr__(self):
        return "Schedule('{}','{}', '{}')".format(
            self.days,
            self.onTime,
            self.onAction,
            self.offTime,
            self.offAction,
            self.noneReset,
            self.updateTime
        )


    def datetime_parser(self, dct):
        format = "%Y-%m-%d %H:%M:%S"
        for k, v in dct.items():
            if k == "onTime" or k == "offTime" or k == "updateTime" or k in "time":
                try:
                    dct[k] = datetime.strptime(v, format)
                except:
                    traceback.print_exc(file=sys.stdout)
        return dct

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return dic

    def datetime_handler(self, x):
        if isinstance(x, (datetime, date)):
            try:
                xd = x.isoformat().replace("T", " ")
                return xd
            except Exception:
                traceback.print_exc(file=sys.stdout)
        raise TypeError("Unknown type")

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr