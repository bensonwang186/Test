import json
import sys
import traceback

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.ext.declarative import declarative_base

from System import settings
from model_Json import DBSession

Base = declarative_base()


class OAuthCredentials(Base):
    __tablename__ = "OAuthCredentials"

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    accessToken = Column(TEXT, nullable=True)
    clientId = Column(TEXT, nullable=True)
    clientSecret = Column(TEXT, nullable=True)
    refreshToken = Column(TEXT, nullable=True)
    tokenExpiry = Column(TEXT, nullable=True)
    tokenUri = Column(TEXT, nullable=True)
    oauthUserEmail = Column(TEXT, nullable=True)

    def __init__(self, jsonString=None):
        self.id = None
        self.accessToken= None
        self.clientId= None
        self.clientSecret= None
        self.refreshToken= None
        self.tokenExpiry= None
        self.tokenUri= None
        self.oauthUserEmail= None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def setOAuthCredentials(self, OAuthCredentials):
        pass
        with DBSession.db_session(settings.PPPE_DB) as session:
            sqlData = session.query(OAuthCredentials).first()

            sqlData.accessToken = self.accessToken = OAuthCredentials.accessToken
            sqlData.clientId = self.clientId = OAuthCredentials.clientId
            sqlData.clientSecret = self.clientSecret = OAuthCredentials.clientSecret
            sqlData.refreshToken = self.refreshToken = OAuthCredentials.refreshToken
            sqlData.tokenExpiry = self.tokenExpiry = OAuthCredentials.tokenExpiry
            sqlData.tokenUri = self.tokenUri = OAuthCredentials.tokenUri
            sqlData.oauthUserEmail = self.oauthUserEmail = OAuthCredentials.oauthUserEmail
            sqlData.senderName = self.senderName = OAuthCredentials.senderName

            session.commit()
            session.close()

    def __repr__(self):
        return "OAuthCredentials('{}','{}', '{}')".format(
            self.accessToken,
            self.clientId,
            self.clientSecret,
            self.refreshToken,
            self.tokenExpiry,
            self.tokenUri,
            self.oauthUserEmail
        )

    def toJson(self):
        d = self.objectAsDict(self)
        try:
            strr = json.dumps(d)
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return strr
