from default import *

from encryptions import *

class ClientInterface:
    def __init__(self, client_socket: socket.socket, client_addr: tuple):
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.username = None

    def get_request(self) -> dict or None:
        """
        get the request from the client
        {
            "cmd": "str"
            data:{
            "str": "str}
        }
        :return: dict of requests or None
        """
        try:
            data = self.client_socket.recv(1024)
            print(data)
            data = decrypt_message(data)  # Returns a decrypted string (JSON)
            if not data:
                return None
            return json.loads(data)  # Convert JSON string to dict
        except Exception as e:
            print("Error receiving data:", e)
            return None

    def send_response(self, cmd:str, code: int, msg: str, data={}) -> bool:
        """
        send a response to the client
        :param cmd: request cmd
        :param code: status code
        :param msg: status code information
        :param data: response data
        :return: true if response was sent, false otherwise
        """

        response = {
            "cmd": cmd,
            "code": code,
            "msg": msg,
            "data": data
        }
        response = json.dumps(response)
        sent = self.client_socket.send(encrypt_message(str(response)))

        return sent == len(response)


