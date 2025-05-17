# encryption.py
from cryptography import fernet
from cryptography.fernet import Fernet

# Shared key
key = b'Y1RR1fC2Yswzw9-0iiEIFR3OupeQCg0UWyEZg9CY6LQ='

cipher = Fernet(key)

def encrypt_message(message: str) -> bytes:
    """Encrypt a string message into bytes."""
    return cipher.encrypt(message.encode('utf-8'))

def decrypt_message(token: bytes) -> str:
    """Decrypt bytes back into a string."""
    return cipher.decrypt(token).decode('utf-8')

