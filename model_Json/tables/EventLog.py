import traceback
import sys
from datetime import date, datetime

from sqlalchemy import Column, inspect, ForeignKey
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import json


Base = declarative_base()


class EventLog(Base):
    __tablename__ = 'EventLog'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    EventId = Column(INTEGER, nullable=False)
    CreateTime = Column(DATETIME, nullable=False)
    Duration = Column(INTEGER, nullable=False)
    isHwFault = Column(BOOLEAN, nullable=True)
    levelCode = Column(TEXT, nullable=True)
    errorCode = Column(TEXT, nullable=True)
    # EventEnum = relationship("EventEnum")

    # def __init__(self, eventId, createTime, duration, jsonString=None):
    #     self.EventId = eventId
    #     self.CreateTime = createTime
    #     self.Duration = duration
    #     if jsonString:
    #         self.__dict__ = json.loads(jsonString, object_hook=self.datetime_parser)

    def __init__(self, jsonString=None):
        self.EventId = None
        self.CreateTime = None
        self.Duration = None
        self.isHwFault = None
        self.levelCode = None
        self.errorCode = None

        if jsonString:
            self.__dict__ = json.loads(jsonString, object_hook=self.datetime_parser)

    def __repr__(self):
        return "EventLog('{}','{}', '{}', '{}', '{}', '{}')".format(
            self.EventId,
            self.CreateTime,
            self.Duration,
            self.isHwFault,
            self.levelCode,
            self.errorCode
        )

    def datetime_parser(self, dct):
        format = "%Y-%m-%d %H:%M:%S"
        for k, v in dct.items():
            if k == "CreateTime" :
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

Index('event_log_id_createTime_idx', EventLog.id, EventLog.CreateTime)

class EventEnum(Base):
    __tablename__ = 'EventEnum'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    reasoning = Column(TEXT, nullable=True)
    # number = Column(INTEGER, ForeignKey('EventLog.EventId'), nullable=True)
    number = Column(INTEGER, nullable=True)
    weight = Column(INTEGER, nullable=True)
    status = Column(INTEGER, nullable=True)
    category = Column(TEXT, nullable=True)
    is_cloud_display = Column(BOOLEAN, nullable=True)
    description = Column(TEXT, nullable=True)
    is_log = Column(BOOLEAN, nullable=True)

    def __init__(self, jsonString=None):
        self.reasoning = None
        self.number = None
        self.weight = None
        self.status = None
        self.category = None
        self.is_cloud_display = None
        self.description = None
        self.is_log = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def __repr__(self):  # control what this function returns for its instances.
        return "EventEnum('{}','{}','{}','{}','{}','{}','{}','{}')".format(
            self.reasoning,
            self.number,
            self.weight,
            self.status,
            self.category,
            self.is_cloud_display,
            self.description,
            self.is_log
        )


    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return dic

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            jsonString = json.dumps(d)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return jsonString