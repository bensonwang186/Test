from System import systemFunction
from model_Json.DevicePushMessageData import SilenceMessage

class EventMoble(object):
    def __init__(self, device):
        self.eventEnum = device.eventEnum
        self.category_Dic = self.GenCategoryDic()

        # I = Input Line Status
        # O = Output Line Status 
        # U = UPS Status
        # B = Battery Status
        # D = Diagnostics
        # C = UPS Communication
        # U1 = UPS Status
        # B1 = Battery Status
        # H = Hardware Fault
        # E = etc. 
        self.I_Array = self.GenCategoryArr("I")
        self.O_Array = self.GenCategoryArr("O")
        self.U_Array = self.GenCategoryArr("U")
        self.B_Array = self.GenCategoryArr("B")
        self.D_Array = self.GenCategoryArr("D")
        self.C_Array = self.GenCategoryArr("C")
        self.U1_Array = self.GenCategoryArr("U1")
        self.B1_Array = self.GenCategoryArr("B1")
        self.H_Array = self.GenCategoryArr("H")
        self.E_Array = self.GenCategoryArr("E")

        # test = self.GetMultiEventsObj(['ID_COMMUNICATION_LOST', 'ID_UTILITY_FAILURE', 'ID_AVR_BUCK_RESTORE',
        # 'ID_UPS_OFF','ID_UPS_SLEEP','ID_A_SCHEDULE_HAS_INITIATED','ID_SHUTDOWN_INITIATED','ID_SYSTEM_IS_OVERHEATED','ID_OUTPUT_CIRCUIT-SHORT','ID_REMAINING_RUNTIME_IS_NO_LONGER_EXHAUSTED'])
        # pass

        # x = self.HexStringToBoolArray("FFC0FFC0FFFEFFFFFF00FFFE0000000000000000")
        # pass

    def GenCategoryArr(self, category):
        temp = list(filter(lambda x: x.category == category, self.eventEnum))
        result = list(map(lambda x: x.reasoning, temp))
        result.reverse()
        return result

    def GenCategoryDic(self):
        result = dict((item.reasoning, item.category) for item in self.eventEnum)
        return result  # key: reasoning; value: category

    def GetCategory(self, EventID_Text):
        category = ''
        if EventID_Text in self.category_Dic:
            category = self.category_Dic[EventID_Text]
        return category

    def GetIndex(self, EventID_Text):
        index = -1
        category = self.GetCategory(EventID_Text)
        if systemFunction.stringIsNullorEmpty(category) == False:
            if category == "I":
                index = self.I_Array.index(EventID_Text)
            if category == "O":
                index = self.O_Array.index(EventID_Text)
            if category == "U":
                index = self.U_Array.index(EventID_Text)
            if category == "B":
                index = self.B_Array.index(EventID_Text)
            if category == "D":
                index = self.D_Array.index(EventID_Text)
            if category == "C":
                index = self.C_Array.index(EventID_Text)
            if category == "U1":
                index = self.U1_Array.index(EventID_Text)
            if category == "B1":
                index = self.B1_Array.index(EventID_Text)
            if category == "H":
                index = self.H_Array.index(EventID_Text)
            if category == "E":
                index = self.E_Array.index(EventID_Text)
        return index

    def GetBinaryStr(self, indexArr):
        resultStr = ''
        resultArr = []

        # generate 0,1 array, ex: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]
        for inx in range(0, 16):  # range(0, 16)指0~15, 不包含16
            if inx in indexArr:
                resultArr.append(1)
            else:
                resultArr.append(0)

        # parse 0,1 array to string, ex: '0000 0000 0000 0011'
        for inx, element in enumerate(resultArr):
            if (inx + 1) is not len(resultArr) and (inx + 1) % 4 == 0:
                resultStr += str(element) + ' '
            else:
                resultStr += str(element)

        return resultStr

    def GetHexStr(self, binaryStr):
        result = ''
        if systemFunction.stringIsNullorEmpty(binaryStr) == False:
            bstr = binaryStr.replace(' ', '')
            result = '%0*X' % ((len(bstr) + 3) // 4, int(bstr, 2))

            # The first line is just cleaning up the binary string.
            # The second line formats it as a hexadecimal string,
            # padded to (len(bstr) + 3) // 4 hex digits,
            # which is number of bits / 4 rounded up,
            # i.e. the number of hex digits required.
            # The last part of the second line parses the binary string to a number,
            # because the %X format specifier is for numbers not binary strings.

        return result  # Hex string

    def GetEventObj(self, EventID_Text):
        result = SilenceMessage.Event()

        indexArr = []
        indexArr.append(self.GetIndex(EventID_Text))

        if len(indexArr) > 0:
            binStr = self.GetBinaryStr(indexArr)
            hexStr = self.GetHexStr(binStr)

        category = self.GetCategory(EventID_Text)
        if systemFunction.stringIsNullorEmpty(category) == False:
            if category == "I":
                result.I = hexStr
            if category == "O":
                result.O = hexStr
            if category == "U":
                result.U = hexStr
            if category == "B":
                result.B = hexStr
            if category == "D":
                result.D = hexStr
            if category == "C":
                result.C = hexStr
            if category == "U1":
                result.U1 = hexStr
            if category == "B1":
                result.B1 = hexStr
            if category == "H":
                result.H = hexStr
            if category == "E":
                result.E = hexStr

        return result

    def GetMultiEventsObj(self, EventID_ARRAY):
        result = SilenceMessage.Event()

        indexDict = dict()
        for idx,val in enumerate(EventID_ARRAY):
            category = self.GetCategory(val)

            if category in indexDict.keys():
                indexDict[category].append(self.GetIndex(val))
            else:
                indexDict[category] = [self.GetIndex(val)]

        for key, value in indexDict.items():

            if len(value) > 0:
                binStr = self.GetBinaryStr(value)
                hexStr = self.GetHexStr(binStr)

            if systemFunction.stringIsNullorEmpty(key) == False:
                if key == "I":
                    result.I = hexStr
                if key == "O":
                    result.O = hexStr
                if key == "U":
                    result.U = hexStr
                if key == "B":
                    result.B = hexStr
                if key == "D":
                    result.D = hexStr
                if key == "C":
                    result.C = hexStr
                if key == "U1":
                    result.U1 = hexStr
                if key == "B1":
                    result.B1 = hexStr
                if key == "H":
                    result.H = hexStr
                if key == "E":
                    result.E = hexStr

        return result

class EventCloud(object):
    def __init__(self, device):
        self.eventEnum = device.eventEnum
        self.category_Dic = self.GenCategoryDic()

        # I = Input Line Status
        # O = Output Line Status 
        # U = UPS Status
        # B = Battery Status
        # D = Diagnostics
        # C = UPS Communication
        # U1 = UPS Status
        # B1 = Battery Status
        # H = Hardware Fault
        # E = etc. 
        self.I_Array = self.GenCategoryArr("I")
        self.O_Array = self.GenCategoryArr("O")
        self.U_Array = self.GenCategoryArr("U")
        self.B_Array = self.GenCategoryArr("B")
        self.D_Array = self.GenCategoryArr("D")
        self.C_Array = self.GenCategoryArr("C")
        self.U1_Array = self.GenCategoryArr("U1")
        self.B1_Array = self.GenCategoryArr("B1")
        self.H_Array = self.GenCategoryArr("H")
        self.E_Array = self.GenCategoryArr("E")

        # test = self.GetMultiEventsObj(['ID_COMMUNICATION_LOST', 'ID_UTILITY_FAILURE', 'ID_AVR_BUCK_RESTORE',
        # 'ID_UPS_OFF','ID_UPS_SLEEP','ID_SCHEDULE_EXPIRED','ID_SHUTDOWN_INITIATED','ID_SYSTEM_OVERHEAT','ID_OUTPUT_CIRCUIT-SHORT','ID_RUNTIME_NOT_EXCEED'])
        # pass

        # x = self.HexStringToBoolArray("FFC0FFC0FFFEFFFFFF00FFFE0000000000000000")
        # pass

    def GenCategoryArr(self, category):
        temp = list(filter(lambda x: x.category == category, self.eventEnum))
        result = list(map(lambda x: x.number, temp))
        result.reverse()
        return result

    def GenCategoryDic(self):
        result = dict((item.number, item.category) for item in self.eventEnum)
        return result  # key: number; value: category


    def GetCategory(self, EventID_Val):
        category = ''
        if EventID_Val in self.category_Dic:
            category = self.category_Dic[EventID_Val]
        return category

    def GetIndex(self, EventID_Val):
        index = -1
        category = self.GetCategory(EventID_Val)
        if systemFunction.stringIsNullorEmpty(category) == False:
            if category == "I":
                index = self.I_Array.index(EventID_Val)
            if category == "O":
                index = self.O_Array.index(EventID_Val)
            if category == "U":
                index = self.U_Array.index(EventID_Val)
            if category == "B":
                index = self.B_Array.index(EventID_Val)
            if category == "D":
                index = self.D_Array.index(EventID_Val)
            if category == "C":
                index = self.C_Array.index(EventID_Val)
            if category == "U1":
                index = self.U1_Array.index(EventID_Val)
            if category == "B1":
                index = self.B1_Array.index(EventID_Val)
            if category == "H":
                index = self.H_Array.index(EventID_Val)
            if category == "E":
                index = self.E_Array.index(EventID_Val)
        return index

    def GetBinaryStr(self, indexArr):
        resultStr = ''
        resultArr = []

        # generate 0,1 array, ex: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]
        for inx in range(0, 16):  # range(0, 16)指0~15, 不包含16
            if inx in indexArr:
                resultArr.append(1)
            else:
                resultArr.append(0)

        # parse 0,1 array to string, ex: '0000 0000 0000 0011'
        for inx, element in enumerate(resultArr):
            if (inx + 1) is not len(resultArr) and (inx + 1) % 4 == 0:
                resultStr += str(element) + ' '
            else:
                resultStr += str(element)

        return resultStr

    def GetHexStr(self, binaryStr):
        result = ''
        if systemFunction.stringIsNullorEmpty(binaryStr) == False:
            bstr = binaryStr.replace(' ', '')
            result = '%0*X' % ((len(bstr) + 3) // 4, int(bstr, 2))

            # The first line is just cleaning up the binary string.
            # The second line formats it as a hexadecimal string,
            # padded to (len(bstr) + 3) // 4 hex digits,
            # which is number of bits / 4 rounded up,
            # i.e. the number of hex digits required.
            # The last part of the second line parses the binary string to a number,
            # because the %X format specifier is for numbers not binary strings.

        return result  # Hex string

    def GetEventObj(self, eventNumArray):
        result = SilenceMessage.Event()

        indexDict = dict()
        for idx, val in enumerate(eventNumArray):
            category = self.GetCategory(val)

            if category in indexDict.keys():
                indexDict[category].append(self.GetIndex(val))
            else:
                indexDict[category] = [self.GetIndex(val)]

        for key, value in indexDict.items():

            if len(value) > 0:
                binStr = self.GetBinaryStr(value)
                hexStr = self.GetHexStr(binStr)

            if systemFunction.stringIsNullorEmpty(key) == False:
                if key == "I":
                    result.I = hexStr
                if key == "O":
                    result.O = hexStr
                if key == "U":
                    result.U = hexStr
                if key == "B":
                    result.B = hexStr
                if key == "D":
                    result.D = hexStr
                if key == "C":
                    result.C = hexStr
                if key == "U1":
                    result.U1 = hexStr
                if key == "B1":
                    result.B1 = hexStr
                if key == "H":
                    result.H = hexStr
                if key == "E":
                    result.E = hexStr

        return result



