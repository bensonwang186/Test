
class BypassEventCount:

    def __init__(self):
        self.BYPASS_ACTIVE_OCCUR_EVENT = 4
        self.BYPASS_ACTIVE_FAKE_OCCUR = 1
        # self.MANUAL_BYPASS_OCCUR_EVENT = 1
        self.ENTER_ECOMODE_OCCUR_EVENT = 2
        self.ENTER_ECOMODE_FAKE_OCCUR = 1

        self.bypassActiveCount = 0
        # self.manualBypassCount = 0
        self.enterECOModeCount = 0

    # 3個時間點reset: 1.休眠下, 市電恢復 2.UPS斷線時(enter hibernation)  3.UPS第一次連線
    def reset(self):
        self.bypassActiveCount = 0
        # self.manualBypassCount = 0
        self.enterECOModeCount = 0

    def checkBypassActive(self, value):
        if value == 1 and not self.isEnterECOModeEverOccur():
            if self.bypassActiveCount < self.BYPASS_ACTIVE_OCCUR_EVENT:
                self.bypassActiveCount += 1
        else:
            self.clearBypassActiveCount()

        return self.isBypassActiveOccur()


    def checkECOMode(self, value):
        if value == 1:
            if self.enterECOModeCount < self.ENTER_ECOMODE_OCCUR_EVENT:
                self.enterECOModeCount += 1

            self.clearBypassActiveCount()
        else:
            self.clearEnterECOModeCount()

        return self.isEnterECOModeOccur()

    def clearBypassActiveCount(self):
        self.bypassActiveCount = 0

    def clearEnterECOModeCount(self):
        self.enterECOModeCount = 0

    def isBypassActiveEverOccur(self):
        return (self.bypassActiveCount >= self.BYPASS_ACTIVE_FAKE_OCCUR) and (self.bypassActiveCount <= self.BYPASS_ACTIVE_OCCUR_EVENT)

    def isEnterECOModeEverOccur(self):
        return (self.enterECOModeCount >= self.ENTER_ECOMODE_FAKE_OCCUR) and (self.enterECOModeCount <= self.ENTER_ECOMODE_OCCUR_EVENT)

    def isBypassActiveOccur(self):
        if self.bypassActiveCount == self.BYPASS_ACTIVE_OCCUR_EVENT:
            return 1
        else:
            return 0

    def isEnterECOModeOccur(self):
        if self.enterECOModeCount == self.ENTER_ECOMODE_OCCUR_EVENT:
            return 1
        else:
            return 0
