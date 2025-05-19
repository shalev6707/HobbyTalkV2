from typing import Tuple

from default import *
from encryptions import *

class Client:
    def __init__(self):
        self.svr_host = "192.168.1.125"
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
            # Prepare request message
            message = {
                "cmd": cmd,
                "data": data
            }

            # Convert to JSON and encrypt
            json_message = json.dumps(message)
            encrypted_message = encrypt_message(json_message)
            print(encrypted_message)

            # Send encrypted message
            self.sock.sendall(encrypted_message)

            # Receive and decrypt response
            encrypted_response = self.sock.recv(4096)  # Consider increasing buffer size
            decrypted_response = decrypt_message(encrypted_response)  # Returns string

            if not decrypted_response:
                return False, {}

            response_data = json.loads(decrypted_response)  # Convert JSON string to dict
            success = response_data.get("code") == 200
            return success, response_data.get("data", {})

        except Exception as e:
            print("Send request error:", e)
            return False, {}

if __name__ == '__main__':
    client = Client()