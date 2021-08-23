import sys
import json
import traceback
from datetime import date, datetime

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = 'Account'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    accountId = Column(TEXT, nullable=True)
    accountSecret = Column(TEXT, nullable=True)
    fcmApiKey = Column(TEXT, nullable=True)
    emqAcc = Column(TEXT, nullable=True)
    emqSecret = Column(TEXT, nullable=True)
    acode = Column(INTEGER, nullable=True)

    def __init__(self, jsonString=None):
        self.accountId = None
        self.accountSecret = None
        self.fcmApiKey = None
        self.emqAcc = None
        self.emqSecret = None
        self.acode = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def __repr__(self):  # control what this function returns for its instances.
        return "Account('{}','{}', '{}')".format(
            self.accountId,
            self.accountSecret,
            self.fcmApiKey,
            self.emqAcc,
            self.emqSecret,
            self.acode
        )

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        return dic

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr
