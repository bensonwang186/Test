import traceback
import sys
from datetime import date, datetime

from sqlalchemy import Column, inspect, ForeignKey
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, BOOLEAN, FLOAT, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json


Base = declarative_base()

class HardwareFaultCodeInfo(Base):
    __tablename__ = 'HardwareFaultCodeInfo'

    Id = Column(INTEGER, autoincrement=True, primary_key=True)
    ErrorCode = Column(TEXT, nullable=False)
    Description = Column(TEXT, nullable=False)
    Note = Column(TEXT, nullable=True)
    IsActive = Column(BOOLEAN, nullable=False)

    def __init__(self, jsonString=None):
        self.ErrorCode = None
        self.Description = None
        self.Note = None
        self.IsActive = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def __repr__(self):  # control what this function returns for its instances.
        return "HardwareFaultCodeInfo('{}','{}','{}','{}')".format(
            self.ErrorCode,
            self.Description,
            self.Note,
            self.IsActive
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

class HardwareFaultLevelInfo(Base):
    __tablename__ = 'HardwareFaultLevelInfo'

    Id = Column(INTEGER, autoincrement=True, primary_key=True)
    Level = Column(INTEGER, nullable=False)
    LevelCode = Column(TEXT, nullable=False)
    ColorCode = Column(TEXT, nullable=False)
    Note = Column(TEXT, nullable=True)

    def __init__(self, jsonString=None):
        self.Level = None
        self.LevelCode = None
        self.ColorCode = None
        self.Note = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def __repr__(self):  # control what this function returns for its instances.
        return "HardwareFaultLevelInfo('{}','{}','{}','{}')".format(
            self.Level,
            self.LevelCode,
            self.ColorCode,
            self.Note
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