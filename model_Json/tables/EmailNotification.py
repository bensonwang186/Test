import json

from sqlalchemy import Column, inspect
from sqlalchemy.dialects.sqlite import BOOLEAN
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base

from System import settings
from model_Json import DBSession

Base = declarative_base()


class EmailNotification(Base):
    __tablename__ = 'EmailNotification'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    active = Column(BOOLEAN, nullable=False)
    serviceProvider = Column(INTEGER, nullable=False)
    smtpServiceAddress = Column(TEXT, nullable=True)
    securityConnection = Column(INTEGER, nullable=True)
    servicePort = Column(INTEGER, nullable=True)
    senderName = Column(TEXT, nullable=True)
    senderEmailAddress = Column(TEXT, nullable=True)
    needAuth = Column(BOOLEAN, nullable=True)
    authAccount = Column(TEXT, nullable=True)
    authPassword = Column(TEXT, nullable=True)
    receivers = Column(TEXT, nullable=True)
    isApplied = Column(BOOLEAN, nullable=False)

    def __init__(self, jsonString = None):
        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def setEmailNotification(self, emailNotification):
        with DBSession.db_session(settings.PPPE_DB) as session:
            sqlData = session.query(EmailNotification).first()
            sqlData.active = self.active = emailNotification.active
            sqlData.serviceProvider = self.serviceProvider = emailNotification.serviceProvider
            sqlData.smtpServiceAddress = self.smtpServiceAddress = emailNotification.smtpServiceAddress
            sqlData.securityConnection = self.securityConnection = emailNotification.securityConnection
            sqlData.servicePort = self.servicePort = emailNotification.servicePort
            sqlData.senderName = self.senderName = emailNotification.senderName
            sqlData.senderEmailAddress = self.senderEmailAddress = emailNotification.senderEmailAddress
            sqlData.needAuth = self.needAuth = emailNotification.needAuth
            sqlData.authAccount = self.authAccount = emailNotification.authAccount
            sqlData.authPassword = self.authPassword = emailNotification.authPassword
            sqlData.receivers = self.receivers = emailNotification.receivers
            sqlData.isApplied = self.isApplied = emailNotification.isApplied

            session.commit()
            session.close()

    def __repr__(self):
        return "EmailNotification('{}','{}', '{}')".format(
            self.active,
            self.serviceProvider,
            self.smtpServiceAddress,
            self.securityConnection,
            self.servicePort,
            self.senderName,
            self.senderEmailAddress,
            self.needAuth,
            self.authAccount,
            self.authPassword,
            self.receivers,
            self.isApplied
        )

    def objectAsDict(self, obj):
        dic = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

        return dic

    def toJson(self):
        d = self.objectAsDict(self)
        return json.dumps(d)