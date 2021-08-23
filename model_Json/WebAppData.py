import json
import traceback
import sys

class AccountMobileLoginItem:

    def __init__(self):
        self._Account = None
        self._Password = None
        self._IP = None
        self._LoginType = None
        self._UpsSn = None
        self._otp = None
        self._AddDeviceParam = self.AddDeviceParam()

    def toJson(self):
        return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
                          separators=(',', ':'))

    @property
    def Account(self):
        return self._Account

    @Account.setter
    def Account(self, value):
        self._Account = value

    @property
    def Password(self):
        return self._Password

    @Password.setter
    def Password(self, value):
        self._Password = value

    @property
    def IP(self):
        return self._IP

    @IP.setter
    def IP(self, value):
        self._IP = value

    @property
    def LoginType(self):
        return self._LoginType

    @LoginType.setter
    def LoginType(self, value):
        self._LoginType = value

    @property
    def UpsSn(self):
        return self._UpsSn

    @UpsSn.setter
    def UpsSn(self, value):
        self._UpsSn = value

    @property
    def otp(self):
        return self._otp

    @otp.setter
    def otp(self, value):
        self._otp = value

    @property
    def AddDeviceParam(self):
        return self._AddDeviceParam

    @AddDeviceParam.setter
    def AddDeviceParam(self, value):
        self._AddDeviceParam = value

    class AddDeviceParam:

        def __init__(self):
            self.Account = None
            self.UniqueId = None
            self.DeviceType = None
            self.DeviceName = None
            self.Model = None
            self.DeviceSn = None
            self.DeviceOS = None
            self.OSVersion = None
            self.DeviceId = None
            self.CreateUser = None

class UpdateDeviceParam:

    def __init__(self):
        self._Ip = None
        self._Account = None
        self._UniqueId = None
        self._DeviceId = None
        self._OSVersion = None
        self._DeviceName = None
        self._DeviceSn = None

    def toJson(self):
        return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
                          separators=(',', ':'))

    @property
    def Account(self):
        return self._Account

    @Account.setter
    def Account(self, value):
        self._Account = value

    @property
    def UniqueId(self):
        return self._UniqueId

    @UniqueId.setter
    def UniqueId(self, value):
        self._UniqueId = value

    @property
    def Ip(self):
        return self._Ip

    @Ip.setter
    def Ip(self, value):
        self._Ip = value

    @property
    def DeviceId(self):
        return self._DeviceId

    @DeviceId.setter
    def DeviceId(self, value):
        self._DeviceId = value

    @property
    def OSVersion(self):
        return self._OSVersion

    @OSVersion.setter
    def OSVersion(self, value):
        self._OSVersion = value

    @property
    def DeviceName(self):
        return self._DeviceName

    @DeviceName.setter
    def DeviceName(self, value):
        self._DeviceName = value

    @property
    def DeviceSn(self):
        return self._DeviceSn

    @DeviceSn.setter
    def DeviceSn(self, value):
        self._DeviceSn = value

class CheckDuplicateDeviceParam:

    def __init__(self):
        self._AccountName = None
        self._AccountId = None
        self._DeviceName = None
        self._DeviceSn = None

    def toJson(self):
        return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
                          separators=(',', ':'))

    @property
    def Account(self):
        return self._Account

    @Account.setter
    def Account(self, value):
        self._Account = value

    @property
    def AccountId(self):
        return self._AccountId

    @AccountId.setter
    def AccountId(self, value):
        self._AccountId = value

    @property
    def DeviceName(self):
        return self._DeviceName

    @DeviceName.setter
    def DeviceName(self, value):
        self._DeviceName = value

    @property
    def DeviceSn(self):
        return self._DeviceSn

    @DeviceSn.setter
    def DeviceSn(self, value):
        self._DeviceSn = value

class ResponseInfo:

    def __init__(self, jsonString = None):
        super(ResponseInfo, self).__init__()
        self._Flag = None
        self._Message = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    def toJson(self):
        # return json.dumps(self, default=lambda o: {k.lstrip('_'): v for k, v in o.__dict__.items()},
        #                   separators=(',', ':'))
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @property
    def Flag(self):
        return self._Flag

    @Flag.setter
    def Flag(self, value):
        self._Flag = value

    @property
    def Message(self):
        return self._Message

    @Message.setter
    def Message(self, value):
        self._Message = value

class LoginMessage(ResponseInfo):

    def __init__(self, jsonString = None):
        super(LoginMessage, self).__init__()

        self._TopicId = None
        self._OtpKey = None
        self._DevicesInfor = self.PowerPanelDeviceInfor()
        self._freq_constant = None
        self._freq_app_act = None

        if jsonString:
            self.__dict__ = json.loads(jsonString)

    @property
    def TopicId(self):
        return self._TopicId

    @TopicId.setter
    def TopicId(self, value):
        self._TopicId = value

    @property
    def OtpKey(self):
        return self._OtpKey

    @OtpKey.setter
    def OtpKey(self, value):
        self._OtpKey = value

    @property
    def DevicesInfor(self):
        return self._DevicesInfor

    @DevicesInfor.setter
    def DevicesInfor(self, value):
        self._DevicesInfor = value

    @property
    def freq_constant(self):
        return self._freq_constant

    @freq_constant.setter
    def freq_constant(self, value):
        self._freq_constant = value

    @property
    def freq_app_act(self):
        return self._freq_app_act

    @freq_app_act.setter
    def freq_app_act(self, value):
        self._freq_app_act = value

    class PowerPanelDeviceInfor:

        def __init__(self):
            self.Id = None
            self.AccountId = None
            self.DeviceType = None
            self.DeviceName = None
            self.Model = None
            self.DeviceSn = None
            self.DeviceOS = None
            self.OSVersion = None
            self.Region = None
            self.Unique_ID = None
            self.Device_ID = None
            self.CreateUser = None
            self.CreateTime = None
            self.UpdateUser = None
            self.UpdateTime = None
            self.IsActive = None

class AddDeviceLogParam:

    def __init__(self):
        self._dsn = None
        self._logs = None

    def toJson(self):

        try:
            temp = ""
            for item in self.logs:
                s1 = ""
                for attr, value in item.__dict__.items():
                    # print(attr, value)

                    if not attr.startswith("_"):  # remove sqlalchemy orm attribute

                        if value is None:
                            s1 += '"{}":{},'.format(attr, "null")

                        if isinstance(value, (int, float)):
                            s1 += '"{}":{},'.format(attr, str(value))

                        if isinstance(value, str):
                            s1 += '"{}":"{}",'.format(attr, value)

                if s1 != "":
                    s1 = s1[:-1]  # Remove final character
                    temp += "{" + s1 + "},"

            temp = temp[:-1]  # Remove final character
            json_string = "{" + '"dsn":"{}","logs":[{}]'.format(self.dsn, temp) + "}"

            return json_string
        except Exception:
            traceback.print_exc(file=sys.stdout)


    @property
    def dsn(self):
        return self._dsn

    @dsn.setter
    def dsn(self, value):
        self._dsn = value

    @property
    def logs(self):
        return self._logs

    @logs.setter
    def logs(self, value):
        self._logs = value

class CloudLoginData:
    def __init__(self, json_string=None):
        self._connect = None
        self._account = None
        self._password = None
        self._ups_name = None
        self._agree_policy = None
        self._verifiable = None
        if json_string:
            self.__dict__ = json.loads(json_string)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def connect(self):
        return self._connect

    @connect.setter
    def connect(self, value):
        self._connect = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def ups_name(self):
        return self._ups_name

    @ups_name.setter
    def ups_name(self, value):
        self._ups_name = value

    @property
    def agree_policy(self):
        return self._agree_policy

    @agree_policy.setter
    def agree_policy(self, value):
        self._agree_policy = value

    @property
    def verifiable(self):
        return self._verifiable

    @verifiable.setter
    def verifiable(self, value):
        self._verifiable = value