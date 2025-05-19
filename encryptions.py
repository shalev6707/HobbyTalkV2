# encryptions.py

from cryptography.fernet import Fernet

# Shared key – same on client & server
key = b'Y1RR1fC2Yswzw9-0iiEIFR3OupeQCg0UWyEZg9CY6LQ='
cipher = Fernet(key)

def encrypt_message(message: str) -> bytes:
    return cipher.encrypt(message.encode('utf-8'))

def decrypt_message(token: bytes) -> str:
    return cipher.decrypt(token).decode('utf-8')

def encrypt_bytes(data: bytes) -> bytes:
    return cipher.encrypt(data)

def decrypt_bytes(token: bytes) -> bytes:
    return cipher.decrypt(token)
