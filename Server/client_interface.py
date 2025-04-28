from default import *

class ClientInterface:
    def __init__(self, client_socket: socket.socket, client_addr: tuple):
        self.client_socket = client_socket
        self.client_addr = client_addr

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
            data = self.client_socket.recv(1024).decode()
            if not data:
                return None
            return json.loads(data)
        except Exception as e:
            print(f"Error getting request: {e}")
            return None

    def send_response(self, cmd:str, code: int, msg: str) -> bool:
        """
        send a response to the client
        :param cmd: request cmd
        :param code: status code
        :param msg: status code information
        :return: true if response was sent, false otherwise
        """

        response = {
            "cmd": cmd,
            "code": code,
            "msg": msg
        }
        response = json.dumps(response).encode()
        sent = self.client_socket.send(response)
        return sent == len(response)

