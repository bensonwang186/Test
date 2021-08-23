import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Cryptor:
    """
    """
    def __init__(self):
        pass
    def get_key(self, password):
        # password = b"cyberpower123456"
        salt = b"0123456789abcdef"
        #salt = os.urandom(16)
        kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=10000,
                backend=default_backend()
                )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    def enc(self, message):
        f = Fernet(self.get_key(b"cps_softP08"))
        return f.encrypt(message.encode()).decode()

    def dec(self, token):
        f = Fernet(self.get_key(b"cps_softP08"))
        return f.decrypt(token.encode())

    def decToString(self, token):
        decByte = self.dec(token)
        return decByte.decode()



if __name__ == "__main__":
    cc = Cryptor()
    token = cc.enc(b"aaa")
    print(cc.dec(token))