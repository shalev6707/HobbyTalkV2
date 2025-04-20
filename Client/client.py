from default import *

class Client:
    def __init__(self):
        self.svr_host = "127.0.0.1"
        self.svr_port = 8080
        try:
            self.sock = socket.socket()
            self.sock.connect((self.svr_host, self.svr_port))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    client = Client()