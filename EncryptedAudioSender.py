# EncryptedAudioSender (subclass of vidstream.AudioSender)

import socket
from encryptions import encrypt_bytes
from vidstream import AudioSender

class EncryptedAudioSender(AudioSender):
    def _AudioSender__client_streaming(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._AudioSender__host, self._AudioSender__port))
        self._AudioSender__sending_socket = sock
        self._AudioSender__streaming = True

        while self._AudioSender__streaming:
            chunk = self._AudioSender__stream.read(self._AudioSender__chunk)
            encrypted = encrypt_bytes(chunk)
            sock.sendall(encrypted)

        sock.close()
