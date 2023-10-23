import hashlib
import os

default_salt = '00000'.encode()


class User:
    def __init__(self, name, password, salt=default_salt):
        # 使用 SHA-256 和盐值进行加盐哈希加密
        if salt != default_salt:
            self.salt = os.urandom(16)
        else:
            self.salt = default_salt
        self.user_name = name
        self.user_password = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000).hex()


default_user = User(name='anonymous', password='password')
