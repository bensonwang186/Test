import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import BOOLEAN
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Configuration(Base):
    __tablename__ = 'Configuration'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    summaryFilter = Column(INTEGER, nullable=True)
    summaryFilterTime = Column(DATETIME, nullable=True)
    softwareSoundEnable = Column(BOOLEAN, nullable=True)
    softwareSoundTime = Column(DATETIME, nullable=True)
    runtimeType = Column(INTEGER, nullable=True)
    runtimeCountdownTime = Column(INTEGER, nullable=True)
    runtimeTime = Column(DATETIME, nullable=True)
    selfTestResult = Column(BOOLEAN, nullable=True)
    selfTestTime = Column(DATETIME, nullable=True)
    shutDownType = Column(INTEGER, nullable=True)
    shutDownTime = Column(DATETIME, nullable=True)
    IsActive = Column(BOOLEAN, nullable=False)
    mobileSolutionEnable = Column(BOOLEAN, nullable=False)
    customUpsName = Column(TEXT, nullable=True)
    langSetting = Column(TEXT, nullable=True)
    isBattNeedReplaced = Column(BOOLEAN, nullable=False)
    pwdKey = Column(TEXT, nullable=False)
    updateResult = Column(TEXT, nullable=True)
    agree_policy = Column(TEXT, nullable=True)


    def __init__(self, jsonString=None):
        self.summaryFilter = None
        self.summaryFilterTime = None
        self.softwareSoundEnable = None
        self.softwareSoundTime = None
        self.runtimeType = None
        self.runtimeCountdownTime = None
        self.runtimeTime = None
        self.selfTestResult = None
        self.selfTestTime = None
        self.shutDownType = None
        self.shutDownTime = None
        self.IsActive = None
        self.mobileSolutionEnable = None
        self.customUpsName = None
        self.langSetting = None
        self.isBattNeedReplaced = None
        self.pwdKey = None
        self.updateResult = None
        self.agree_policy = None

        if jsonString:
            self.__dict__ = json.loads(jsonString, object_hook = self.datetime_parser)

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
            if k == "selfTestTime":
                try:
                    if v is not None:
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
            except Exception:
                traceback.print_exc(file=sys.stdout)
            return xd
        raise TypeError("Unknown type")

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            jsonString = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return jsonString