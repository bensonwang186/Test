import requests
import os
import RootDir
import hashlib
from System import systemDefine
from Utility import Logger
import platform
class RequestImp:

    def __init__(self, verify=True):
        self.isVerify = True
        self.caHash = "31450F875B46BBBB8E8D2F2E075F82AB4CFE175DADD966BE22C66206D5DC2517A870A8CFC46F2F094B6810C09B447BD46354B67C128843B997957522D3CF4F5F"

    def get(self, url, params=None, **kwargs):
        if systemDefine.MODE == systemDefine.ExcutionMode.PRODUCTION and not self.verifyCaFile():
            # log
            Logger.LogIns().logger.info("Verify Certificate file error")
            raise Exception("Verify Certificate file error")
        # always need verify
        kwargs["verify"] = self.isVerify
        return requests.get(url, params=None, **kwargs)

    def post(self, url, data = None, json = None, ** kwargs):
        # check pem checksum
        # check this in git wiki Personal ca cert驗證機制
        if systemDefine.MODE == systemDefine.ExcutionMode.PRODUCTION and not self.verifyCaFile():
            # log
            Logger.LogIns().logger.info("Verify Certificate file error")
            raise Exception("Verify Certificate file error")
        # always need verify
        kwargs["verify"] = self.isVerify
        print(kwargs)
        return requests.post(url, data=data, json=json, ** kwargs)

    def verifyCaFile(self):
        dir_path = RootDir.PROJECT_ROOT_PATH
        if platform.system() == 'Darwin':
            cafile = os.path.join(dir_path, "lib", "certifi", "cacert.pem")
        else:
            cafile = os.path.join(dir_path, "certifi", "cacert.pem")
        if hashlib.sha512(open(cafile, 'rb').read()).hexdigest().upper() == self.caHash.upper():
            return True
        return False

if __name__ == "__main__":
    dir_path = RootDir.PROJECT_ROOT_PATH
    cafile = os.path.join(dir_path, "cacert.pem")
    print(hashlib.sha512(open(cafile, 'rb').read()).hexdigest())
    print("hi")


# if __name__ == "__main__":
#
#     dir_path = RootDir.PROJECT_ROOT_PATH
#     cafile = os.path.join(dir_path,"cacert.pem")
#     with open(cafile, 'rb') as f:
#         certs = pem.parse(f.read())
#         print(certs)
#     RequestImp.post("",A=1234, B=4321)
#     print(123)