import logging
import threading

from System import systemDefine, systemFunction
from model_Json import Transaction, DriverTransaction, Statement


class TransactionHelper(systemDefine.Singleton):
    def __init__(self):
        self.driverTransaction = DriverTransaction.DriverTransaction()
        self.stop = False
        self._lock = threading.Lock()

    def start(self):
        flag = self.driverTransaction.start()
        return flag

    def stop(self):
        with self._lock:
            if self.stop is True:
                return None

            self.driverTransaction.stop()
            self.stop = True

    def submit(self, trx=Transaction.Transaction):
        with self._lock:
            if self.stop is True:
                return False

        # <editor-fold desc="由transaction將由機器取狀態指令parse出來">

        cmdLine = str(trx.deviceId)

        '''value id field'''
        for stat in trx.statements:
            cmdLine += "\n" + str(stat.Id)

            '''parameters field'''
            if stat.hasParams() is True:
                for param in stat.params:
                    cmdLine += " "
                    cmdLine += str(param)

        cmdLine += "\n"

        # </editor-fold>

        with self._lock:
            respStr = self.driverTransaction.request(cmdLine)

        # <editor-fold desc="Parse由機器傳回來之response, 並重新塞回transaction">

        if ";" not in respStr:
            print('resp error')

        respArr = respStr.split("\n")
        previousStats = list(trx.statements)  # 取出之前存於transaction之statements
        for index, element in enumerate(respArr):
            try:
                if ";" in element:
                    eIndex = element.index(";")
                    front = element[0:eIndex]  # python substring
                    tail = element[int(eIndex + 1):]

                    if index == 0:
                        if systemFunction.intTryParse(front):
                            trx.setDeviceId(int(front))

                        if systemFunction.intTryParse(tail):
                            trx.setState(int(tail))

                        continue

                    else:
                        stat = Statement.Statement()
                        subFronts = front.split(" ")

                        id = -1
                        if len(subFronts) > 0 and systemFunction.intTryParse(subFronts[0]):
                            stat.setId(int(subFronts[0]))
                            id = int(subFronts[0])

                        for i, subFront in enumerate(subFronts):
                            if i > 0 and systemFunction.intTryParse(subFront):
                                stat.params.append(int(subFront))

                        found = False
                        for pre_stat in previousStats:
                            if pre_stat == stat:
                                found = True
                                stat = pre_stat
                                previousStats.remove(pre_stat)

                                break

                        if not found:
                            trx.statements.append(stat)

                        subTails = tail.split(" ")

                        if len(subTails) > 0 and systemFunction.intTryParse(subTails[0]):
                            stat.setErrCode(int(subTails[0]))  # command狀態

                        for i, subTail in enumerate(subTails):
                            if i > 0:
                                stat.results.append(subTail)  # command值

                        """寫入dictionary"""
                        if id >= 0:
                            trx.statementsDic[id] = stat

            except Exception as e:
                logging.exception("message")

        # </editor-fold>

        return True
