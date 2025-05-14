import threading
import pyaudio
import struct

class CallHandler:
    def __init__(self, sock):
        self.socket = sock
        self.running = True

        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.audio = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None

    def start_call(self):
        self.stream_in = self.audio.open(format=self.format, channels=self.channels,
                                         rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.stream_out = self.audio.open(format=self.format, channels=self.channels,
                                          rate=self.rate, output=True, frames_per_buffer=self.chunk)

        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()

    def send_audio(self):
        try:
            while self.running:
                data = self.stream_in.read(self.chunk)
                self.socket.sendall(struct.pack("!I", len(data)) + data)
        except Exception as e:
            print(f"Error sending audio: {e}")
            self.stop_call()

    def receive_audio(self):
        try:
            while self.running:
                length_data = self.socket.recv(4)
                if not length_data:
                    break
                length = struct.unpack("!I", length_data)[0]
                data = self.socket.recv(length)
                if not data:
                    break
                self.stream_out.write(data)
        except Exception as e:
            print(f"Error receiving audio: {e}")
        finally:
            self.stop_call()

    def stop_call(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.audio.terminate()
