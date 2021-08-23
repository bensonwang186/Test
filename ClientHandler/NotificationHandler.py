import sys, traceback
from Utility import OAuthManagement, DataCryptor
from model_Json import DataSource2
from major import Command
from PyQt5.QtCore import QTimer
from Utility import Logger

class NotifycationHandler(object):
    def __init__(self, notifyPage, client, device, tray):
        self.notifyPage = notifyPage
        self.device = device
        self.client = client
        self.tray = tray
        self.authExecutor = OAuthManagement.AuthExecutor()
        self.cacheOauthCredentialsData = None
        self.emailSettingsCache = DataSource2.EmailNotification()
        self.oauthCache = None
        self.verifyingTimer = None
        self.testingTimer = None
        self.oauthingTimer = None


        # == view -> handler start==
        # connect page signal for settings
        self.notifyPage.setNotificationSignal.connect(self.setEmailNotificationSlot)

        # oauth request
        self.notifyPage.oathRequestSignal.connect(self.oauthRequestSlot)

        # oauth exchanged
        self.notifyPage.oathExchangedSignal.connect(self.oauthExchangedSlot)

        self.client.oathExchangedResultSignal.connect(self.oauthExchangedResultSlot)

        # ui refresh
        self.notifyPage.refreshSignal.connect(self.refreshEmailNotification)

        self.notifyPage.sendTestEmailSignal.connect(self.sendTestEmail)

        self.notifyPage.verifyEmailSettingSignal.connect(self.verifyEmailSetting)

        # self.notifyPage.setAlarmEnableSignal.connect(self.setAlarmEnable)


        # == view -> handler end==

        # == handler -> view start==
        # connect email data signal for update

        self.client.notificationEmailUpdataSignal.connect(self.updateEmailNotificationSlot)

        self.client.setVerifyResultSignal.connect(self.verifyEmailSettingResult)

        self.client.sendTestEmailResultSignal.connect(self.sendTestEmailResult)

        # == handler -> view end==
        try:
            self.notifyPage.setUPSAlarmSignal.connect(self.setUPSAlarm)

            self.notifyPage.setSoftSoundSignal.connect(self.setSoftSound)

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def refreshEmailNotification(self):
        emailNotification = self.emailSettingsCache
        oauth = self.oauthCache
        self.updateEmailNotification(emailNotification, oauth)

    def updateEmailNotificationSlot(self, emailNotification, oauthData):
        self.updateEmailNotificationDetail(emailNotification)
        self.updateEmailNotification(emailNotification, oauthData)

    def updateEmailNotification(self, emailNotification, oauthData):
        if emailNotification:
            self.notifyPage.fillEmailData(self.emailSettingsCache)

            # make sure service Provider has data
            if hasattr(emailNotification, "serviceProvider"):
                self.notifyPage.decideShow(emailNotification.serviceProvider)

                # check selected now
                if emailNotification.serviceProvider == DataSource2.EmailServiceProvider.GMAIL.value:
                    # decide show verify button, oauth policy is had applied and authed
                    if oauthData is not None:
                        self.notifyPage.isVerifyEnable(emailNotification.isApplied and oauthData[0])
                    else:
                        self.notifyPage.isVerifyEnable(False)

                elif emailNotification.serviceProvider == DataSource2.EmailServiceProvider.OTHER.value:
                    # decide show verify button
                    self.notifyPage.isVerifyEnable(emailNotification.isApplied)

        if oauthData is not None:
            self.oauthCache = oauthData
            self.notifyPage.decideOauthShowWidget(oauthData[0], oauthData[1])

        print("done")

    def oauthRequestSlot(self):
        self.authExecutor.requestOauthCredentials()

    def oauthExchangedSlot(self, code):
        self.client.queryRequest(Command.TARGET_EXCHANGE_OAUTH, code)

        self.oauthingTimer = QTimer()
        self.oauthingTimer.setSingleShot(True)
        self.oauthingTimer.timeout.connect(self.setOauthExchangeTimeout)
        self.oauthingTimer.start(15000)


    def setOauthExchangeTimeout(self):
        self.notifyPage.oauthVerifyResult(False)

    def oauthExchangedResultSlot(self, oauthCredentials):
        if self.oauthingTimer is not None and self.oauthingTimer.isActive():
            self.oauthingTimer.stop()
        self.cacheOauthCredentialsData = oauthCredentials

        if oauthCredentials:
            self.notifyPage.toogleExchangedSuccessWidget(oauthCredentials)
            self.notifyPage.oauthVerifyResult(True)
        else:
            print("oauth error")
            self.notifyPage.oauthVerifyResult(False)

    def updateEmailNotificationDetail(self, emailNotification):

        try:
            if emailNotification.active is not None:
                self.emailSettingsCache.active = emailNotification.active
            if emailNotification.serviceProvider is not None:
                self.emailSettingsCache.serviceProvider = emailNotification.serviceProvider
            if emailNotification.smtpServiceAddress is not None:
                self.emailSettingsCache.smtpServiceAddress = emailNotification.smtpServiceAddress
            if emailNotification.securityConnection is not None:
                self.emailSettingsCache.securityConnection = emailNotification.securityConnection
            if emailNotification.servicePort is not None:
                self.emailSettingsCache.servicePort = emailNotification.servicePort
            if emailNotification.senderName is not None:
                self.emailSettingsCache.senderName = emailNotification.senderName
            if emailNotification.senderEmailAddress is not None:
                self.emailSettingsCache.senderEmailAddress = emailNotification.senderEmailAddress
            if emailNotification.needAuth is not None:
                self.emailSettingsCache.needAuth = emailNotification.needAuth
            if emailNotification.authAccount is not None:
                self.emailSettingsCache.authAccount = emailNotification.authAccount
            if emailNotification.authPassword is not None:
                cryptor = DataCryptor.Cryptor()
                self.emailSettingsCache.authPassword = cryptor.decToString(emailNotification.authPassword)
            if emailNotification.receivers is not None:
                self.emailSettingsCache.receivers = emailNotification.receivers
            if emailNotification.isApplied is not None:
                self.emailSettingsCache.isApplied = emailNotification.isApplied

            if self.cacheOauthCredentialsData is not None:
                self.oauthCache = [True, self.cacheOauthCredentialsData]

        except Exception:
            Logger.LogIns().logger.error(traceback.format_exc())

    def setEmailNotificationSlot(self, emailNotification):
        cryptor = DataCryptor.Cryptor()

        if emailNotification.authPassword is not None:
            emailNotification.authPassword = cryptor.enc(emailNotification.authPassword)

        self.updateEmailNotificationDetail(emailNotification)
        self.client.queryRequest(Command.TARGET_SET_EMAIL, emailNotification.toJson())
        self.notifyPage.applyResult(True)


    def sendTestEmail(self):
        self.client.queryRequest(Command.TARGET_SET_TEST_EMAIL)

        self.testingTimer = QTimer()
        self.testingTimer.setSingleShot(True)
        self.testingTimer.timeout.connect(self.setTestTimeout)
        self.testingTimer.start(15000)

        # pass
        # Scheduler.SendMailThread("Test Send Mail", self.device.dataSource.emailNotification,
        #                          self.device.dataSource.oauthCredentials, None, True).start()

    def setUPSAlarm(self, param):
        self.client.queryRequest(Command.TARGET_SET_UPS_ALARM, param)

    def setSoftSound(self, param):
        self.tray.softwareSoundEnable = param
        self.client.queryRequest(Command.TARGET_SET_SOFT_SOUND, param)

    def verifyEmailSetting(self):
        self.client.queryRequest(Command.TARGET_SET_VERIFY_EMAIL)

        self.verifyingTimer = QTimer()
        self.verifyingTimer.setSingleShot(True)
        self.verifyingTimer.timeout.connect(self.setVerifyTimeout)
        self.verifyingTimer.start(15000)

    def setVerifyTimeout(self):
        self.notifyPage.verfiyEmailResult(False)

    def verifyEmailSettingResult(self, result):
        self.notifyPage.verfiyEmailResult(result)
        if self.verifyingTimer is not None and self.verifyingTimer.isActive():
            self.verifyingTimer.stop()

    def sendTestEmailResult(self, result):
        self.notifyPage.testingResult(result)
        if self.testingTimer is not None and self.testingTimer.isActive():
            self.testingTimer.stop()

    def setTestTimeout(self):
        self.notifyPage.testingResult(False)

