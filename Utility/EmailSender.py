import webbrowser
import traceback, sys
import smtplib
from Utility import i18nTranslater
from i18n import appLocaleData
import datetime
import os
import httplib2
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from apiclient import errors, discovery
from enum import Enum
from email.header import Header
from email.utils import formataddr
from System import settings
from i18n import i18nId
from Utility import Logger
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

class EmailSecurityConnect(Enum):
    TLS = 0
    SSL = 1
    NONE = 3

class EmailSender(object):
    def __init__(self):
        self.i18nTranslater = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorderFromDB().appLocale)

    def getHtmlFormat(self,headerFile, footerFile, time, content):
        mailHtmlFile = os.path.join(settings.CONTEXT_PATH, "mail.html")
        file = open(mailHtmlFile, 'r')
        html = file.read()
        html = html.replace("KEY_TIME", time)
        html = html.replace("KEY_COTENT", content)
        html = html.replace("HEADER_IMG", headerFile)
        html = html.replace("FOOTER_IMG", footerFile)
        html = html.replace("KEY_Event_Notification", self.i18nTranslater.getTranslateString(i18nId.i18nId().Event_Notification))
        html = html.replace("KEY_Time", self.i18nTranslater.getTranslateString(i18nId.i18nId().Time))
        html = html.replace("KEY_Power_Event_Notification", self.i18nTranslater.getTranslateString(i18nId.i18nId().power_event_notify))
        return html

    def getMessage(self, sender, senderAddr, receiver, subject, time, message):

        messageTitle = "[Power Panel Personal " + subject + "]\r\n"
        timeMessage =i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorderFromDB().appLocale).getTranslateString(i18nId.i18nId().Open) + ": " + time + "\r\n"
        powerEventMessage = subject + ": " + message
        conMessage = messageTitle + timeMessage + powerEventMessage

        headerFile = "logo_powerpanel.png"
        footerFile = "logo_cyberpower.png"

        # Prepare actual message
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = subject
        # msgRoot['From'] = sender+" <"+senderAddr+">"
        msgRoot['From'] = formataddr((str(Header(sender, 'utf-8')), senderAddr))
        msgRoot['To'] = receiver

        msg = MIMEMultipart('alternative')
        msgRoot.attach(msg)
        part1 = MIMEText(conMessage, 'plain')
        part2 = MIMEText(self.getHtmlFormat(headerFile, footerFile, time, message), 'html')
        msg.attach(part1)
        msg.attach(part2)

        headerFileAttachment = os.path.join(settings.CONTEXT_PATH, headerFile)
        footerFileAttachment = os.path.join(settings.CONTEXT_PATH, footerFile)
        fp = open(headerFileAttachment, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<{}>'.format(headerFile))
        msgRoot.attach(img)

        fp = open(footerFileAttachment, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<{}>'.format(footerFile))
        msgRoot.attach(img)

        return msgRoot

    def sendEmail(self, message, snmtpAddr, securityConn, port, senderName, senderAddr, needAuth, authAccount, authPassword, receivers, callBack=None):
        Logger.LogIns().logger.info("start send mail by custom smtp server")
        time = str(datetime.datetime.now().replace(microsecond=0))
        subject = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorderFromDB().appLocale).getTranslateString("power_event_notify")

        FROM = senderAddr
        ToList = receivers.split(',')

        if len(ToList) > 1:
            TO = ", ".join(ToList)

        if len(ToList) == 1:
            TO = ToList.pop(0)

        msgRoot = self.getMessage(senderName, senderAddr, TO, subject, time, message)

        Logger.LogIns().logger.info("send to: " + str(TO))

        try:
            server = None
            if securityConn is EmailSecurityConnect.TLS.value:
                Logger.LogIns().logger.info("using tls")
                server = smtplib.SMTP(snmtpAddr, port)
                Logger.LogIns().logger.info("ehlo tls")
                server.ehlo()
                Logger.LogIns().logger.info("start tls")
                server.starttls()
                server.ehlo()
                Logger.LogIns().logger.info("tls finished")
            elif securityConn is EmailSecurityConnect.SSL.value:
                Logger.LogIns().logger.info("using ssl")
                server = smtplib.SMTP_SSL(snmtpAddr, port)
                Logger.LogIns().logger.info("ehlo ssl")
                server.ehlo()
                Logger.LogIns().logger.info("ssl finished")
            else:
                Logger.LogIns().logger.info("using port 25")
                server = smtplib.SMTP(snmtpAddr, port)
                server.ehlo()
                Logger.LogIns().logger.info("using port 25 finished")
            if needAuth and authAccount != None:
                Logger.LogIns().logger.info("smtp login")
                server.login(authAccount, authPassword)
                Logger.LogIns().logger.info("smtp login finished")

            if server != None:
                # server.sendmail(FROM, TO, message)
                Logger.LogIns().logger.info("smtp send mail")
                server.sendmail(FROM, TO, msgRoot.as_string())
                Logger.LogIns().logger.info("smtp send mail finished")
                result = True
        except Exception:
            result = False
            Logger.LogIns().logger.info("configure sending mail failed")
            Logger.LogIns().logger.info(traceback.format_exc())
        finally:
            if server:
                server.close()
            if callBack:
                callBack(result)


    def requestOauthCredentials(self):
        flow = None
        try:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            auth_uri = flow.step1_get_authorize_url()
            webbrowser.open(auth_uri)
            flow.user_agent = APPLICATION_NAME
        except Exception:
            traceback.print_exc(file=sys.stdout)


    def getCredentials(self, accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri):
        credentials = oauth2client.client.GoogleCredentials(
            accessToken,
            clientId,
            clientSecret,
            refreshToken,
            tokenExpiry,
            tokenUri,
            "PPPE Email Sender",
            "https://accounts.google.com/o/oauth2/revoke")

        return credentials

    def sendEmailByOauth(self, eventMessage, senderName, receivers, accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri, callback, isVerify=False):
        Logger.LogIns().logger.info("start send mail by Oauth")
        credentials = self.getCredentials(accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri)
        http = credentials.authorize(httplib2.Http())
        try:
            Logger.LogIns().logger.info("get send mail service")
            service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
        except Exception:
            Logger.LogIns().logger.info("get send mail service failed")
            Logger.LogIns().logger.info(traceback.format_exc())

        time = str(datetime.datetime.now().replace(microsecond=0))
        subject = i18nTranslater.i18nTranslater(appLocaleData.appLocaleRecorderFromDB().appLocale).getTranslateString("power_event_notify")

        # author = formataddr((str(Header(senderName, 'utf-8')), oauthUserEmail))
        author = senderName
        user_info = self.getOauthUserInfo(accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri)
        oauthUserEmail = ""
        if user_info and user_info.get('email'):
            oauthUserEmail = user_info.get('email')

        ToList = receivers.split(',')
        if len(ToList) > 1:
            TO = ", ".join(ToList)

        if len(ToList) == 1:
            TO = ToList.pop(0)

        if isVerify:
            TO = oauthUserEmail

        Logger.LogIns().logger.info("send to: " + str(TO))
        msgRoot = self.getMessage(author, oauthUserEmail, TO, subject, time, eventMessage)

        raw = base64.urlsafe_b64encode(msgRoot.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}
        try:
            Logger.LogIns().logger.info("send oauth gmail")
            message = (service.users().messages().send(userId="me", body=body).execute())
            Logger.LogIns().logger.info("send message: "+str(message))
            result = True
        except Exception:
            result = False
            Logger.LogIns().logger.info("send oauth gmail failed")
            Logger.LogIns().logger.info(traceback.format_exc())
            traceback.print_exc(file=sys.stdout)
        finally:
            if callback:
                callback(result)

    def getOauthUserInfo(self,accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri):
        credentials = self.getCredentials(accessToken, clientId, clientSecret, refreshToken, tokenExpiry, tokenUri)
        http = credentials.authorize(httplib2.Http())
        user_info_service = discovery.build(serviceName='oauth2', version='v2', http=http, cache_discovery=False)
        user_info = None
        oauthUserEmail = ""
        try:
            Logger.LogIns().logger.info("get user info")
            user_info = user_info_service.userinfo().get().execute()
        except Exception:
            Logger.LogIns().logger.info("get user info error")
            Logger.LogIns().logger.info(traceback.format_exc())

        return user_info