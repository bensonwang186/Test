import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import FLOAT
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EnergyConsumption(Base):
    __tablename__ = 'EnergyConsumption'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    consumption = Column(FLOAT, nullable=True)
    createTime = Column(DATETIME, nullable=True)

    def __init__(self):
        self.consumption = None
        self.createTime = None

    def __repr__(self):
        return "EnergyConsumption('{}','{}', '{}')".format(
            self.consumption,
            self.createTime
        )

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        for subObj in dic.values():
            if isinstance(subObj, (datetime, date)):
                subObj = subObj.isoformat().replace("T", " ")
        return dic

    def datetime_handler(self, x):
        if isinstance(x, datetime):
            return x.isoformat().replace("T", " ")
        raise TypeError("Unknown type")

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d, default=self.datetime_handler)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr