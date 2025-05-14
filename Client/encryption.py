# encryption.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class Encryption:
    def __init__(self, key):
        self.key = key[:32].ljust(32, '0').encode()  # AES-256 key (32 bytes)

    def encrypt_bytes(self, data):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        return cipher.iv + ct_bytes

    def decrypt_bytes(self, data):
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ct), AES.block_size)
