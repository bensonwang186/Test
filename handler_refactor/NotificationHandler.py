import json
import sys
import traceback

from System import systemFunction
from Utility import EmailSender, OAuthManagement, Scheduler
from controllers import DeviceConfigure
from major import Command
from model_Json import DataSource2
from model_Json.tables.Configuration import Configuration


class NotifycationHandler(object):
    def __init__(self, server, device):
        self.server = server
        self.device = device
        self.authExecutor = OAuthManagement.AuthExecutor()

        # if self.device.
        self.cacheOauthCredentialsData = None
        self.oauthSummary = [False, ""]
        self.deviceConfigure = DeviceConfigure.DeviceConfigure()

        # == view -> handler start==
        # connect page signal for settings
        self.server.setNotificationSignal.connect(self.setEmailNotificationSlot)

        self.server.fetchEmailNotificationSignal.connect(self.sendEmailNotification)

        #
        # # oauth request
        # self.notifyPage.oathRequestSignal.connect(self.oauthRequestSlot)
        #
        # # oauth exchanged
        self.server.oathExchangedSignal.connect(self.oauthExchangedSlot)
        #
        # # ui refresh
        # self.notifyPage.refreshSignal.connect(self.refreshEmailNotification)
        #
        self.server.sendTestEmailSignal.connect(self.sendTestEmail)
        #
        self.server.setUPSAlarmSignal.connect(self.setUPSAlarm)

        self.server.setSoftSoundSignal.connect(self.setSoftSound)

        self.server.setVerifySettingsSignal.connect(self.setVerifySettings)

        # self.notifyPage.setAlarmEnableSignal.connect(self.setAlarmEnable)


        # == view -> handler end==

        # == handler -> view start==
        # connect email data signal for update

        # self.device.dataSource.updateEmailNotificationSignal.connect(self.updateEmailNotificationSlot)

        # == handler -> view end==

        self.checkOauthCredential()

    def checkOauthCredential(self):
        oauthCredentials = self.device.dataSource.oauthCredentials
        if oauthCredentials  is not None:
            accessToken = oauthCredentials.accessToken
            clientId = oauthCredentials.clientId
            clientSecret = oauthCredentials.clientSecret
            refreshToken = oauthCredentials.refreshToken
            tokenExpiry = oauthCredentials.tokenExpiry
            tokenUri = oauthCredentials.tokenUri

            if accessToken or clientId or clientSecret or refreshToken or tokenExpiry or tokenUri != None:
                credentials = EmailSender.EmailSender().getCredentials(accessToken, clientId, clientSecret,
                                                                       refreshToken, tokenExpiry, tokenUri)
                try:
                    # if not credentials or credentials.invalid:
                    if credentials or not credentials.invalid:
                        self.oauthSummary[0] = True
                        self.oauthSummary[1] = oauthCredentials.oauthUserEmail
                except Exception:
                    traceback.print_exc(file=sys.stdout)


    def sendEmailNotification(self, clientConnection):
        try:
            notificationSettings = []
            # data = Command.TARGET_NOTIFICATION_EMAIL + self.device.dataSource.emailNotification.toJson()
            notificationSettings.append(self.device.dataSource.emailNotification)
            oauthSettings = []

            oauthSettings.append(self.oauthSummary[0])  # is oauth settings alive
            oauthSettings.append(self.oauthSummary[1])  # is oauth settings alive
            notificationSettings.append(oauthSettings)
            jsonData = json.dumps(notificationSettings, default=systemFunction.jsonSerialize)
            print("Command.TARGET_NOTIFICATION_EMAIL:Command.TARGET_NOTIFICATION_EMAIL:: " + jsonData)
            # data = self.device.dataSource.emailNotification.toJson()
            data = json.dumps(notificationSettings, default=systemFunction.jsonSerialize)
            print("Command.TARGET_NOTIFICATION_EMAIL:" + data)
            self.server.sendToClient(Command.TARGET_NOTIFICATION_EMAIL, data, clientConnection)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def oauthExchangedSlot(self, code):
        self.authExecutor.requestExchange(code, self.sayHello)

    def sayHello(self, errorCode, oauthCredentials):
        self.cacheOauthCredentialsData = oauthCredentials
        print("hello; " + str(errorCode))

        if errorCode == OAuthManagement.OAuthErrorCode.SUCCESS.value:
            print("oauth success")
            self.server.sendDataToClients(Command.TARGET_EXCHANGE_OAUTH, oauthCredentials.oauthUserEmail)
            # self.notifyPage.toogleExchangedSuccessWidget(oauthCredentials.oauthUserEmail)
        else:
            print("oauth error")
            self.server.sendDataToClients(Command.TARGET_EXCHANGE_OAUTH, "")

    def setEmailNotificationSlot(self, emailNotification):
        result = False
        try:
            if emailNotification.serviceProvider == DataSource2.EmailServiceProvider.GMAIL.value:
                self.device.dataSource.setOAuthCredentials(self.cacheOauthCredentialsData)

            self.device.dataSource.setEmailNotification(emailNotification)
            result = True
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def sendTestEmail(self):
        # pass
        Scheduler.SendMailThread("Test Send Mail", self.device.dataSource.emailNotification,
                                 self.device.dataSource.oauthCredentials, None, True, False, self.testSendEmailResultResp).start()

    def setUPSAlarm(self, param):
        configData = self.deviceConfigure.configParam()
        configData.buzzerAllow = 1
        configData.params.append(param)

        print("self.device.deviceId: "+ str(self.device.deviceId))
        if self.device.deviceId != -1:
            flag = self.deviceConfigure.deviceConfigSubmit(configData, self.device.deviceId)

            if flag:
                print("set UPS Alarm success")
            else:
                print("set UPS Alarm fail")

            return flag

    def setSoftSound(self, param):
        try:
            deviceConfigure = DeviceConfigure.DeviceConfigure()
            config = Configuration()
            if param:
                config.softwareSoundEnable = True
                self.device.dataSource.updateDeviceConfig(config)
                # print("CHECKED!")
            else:
                config.softwareSoundEnable = False
                self.device.dataSource.updateDeviceConfig(config)
                # print("UNCHECKED!")
        except Exception:
            traceback.print_exc(file=sys.stdout)

    def setVerifySettings(self):
        Scheduler.SendMailThread("Test Send Mail", self.device.dataSource.emailNotification,
                                 self.device.dataSource.oauthCredentials, None, False, True, self.verifyResultResp).start()

    def verifyResultResp(self, result):
        self.server.sendDataToClients(Command.TARGET_SET_VERIFY_EMAIL, result)

    def testSendEmailResultResp(self, result):
        self.server.sendDataToClients(Command.TARGET_SET_TEST_EMAIL, result)