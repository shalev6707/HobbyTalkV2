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

    def send_request(self, cmd: str, data: dict) -> bool:
        if not self.sock:
            print("Socket not connected.")
            return False

        try:
            # Build the message
            message = {
                "cmd": cmd,
                "data": data
            }
            # Send JSON-encoded data
            json_data = json.dumps(message)
            self.sock.sendall(json_data.encode())

            # Receive and decode server response
            response = self.sock.recv(1024).decode()
            response_data = json.loads(response)

            return response_data.get("cmd") == cmd and response_data.get("code") == 200

        except Exception as e:
            print("Send request error:", e)
            return False


if __name__ == '__main__':
    client = Client()