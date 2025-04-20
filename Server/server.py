from default import *
from client_interface import ClientInterface

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080

        # Create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def run(self):
        """
        Runs the server
        """
        print("Server starting...")
        self.socket.listen()
        while True:
            sock, addr = self.socket.accept()
            client = ClientInterface(sock,addr)
            threading.Thread(target=self.handle_client, args=[client]).start()


    def handle_client(self, client: ClientInterface):
        """
        Handles client connection
        :param client: the client to handle
        """
        print("Client connected")
        while True:
            request = client.get_request()
            if request:
                pass


if __name__ == '__main__':
    s = Server()
    s.run()