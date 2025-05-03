from typing import Tuple

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

    def send_request(self, cmd: str, data: dict) -> Tuple[bool, dict]:
        if not self.sock:
            print("Socket not connected.")
            return False, {}

        try:
            message = {
                "cmd": cmd,
                "data": data
            }
            self.sock.sendall(json.dumps(message).encode())
            response = self.sock.recv(1024).decode()

            if not response:
                return False, {}

            response_data = json.loads(response)
            success = response_data.get("code") == 200
            return success, response_data.get("data", {})

        except Exception as e:
            print("Send request error:", e)
            return False, {}


if __name__ == '__main__':
    client = Client()