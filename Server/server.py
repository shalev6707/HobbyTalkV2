from Server.DataBase.DatabaseManager import DBManager
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
        print("Client connected")
        while True:
            try:
                request = client.get_request()
                if request is None:
                    print("Client disconnected or sent invalid data.")
                    break

                print(f"Received request: {request}")

                if "cmd" not in request or "data" not in request:
                    client.send_response("error", 400, "Invalid request format.")
                    continue

                if request["cmd"] == "register":
                    try:
                        DBManager.write("users", request["data"])
                        client.send_response("register", 200, "Registration was successful")
                    except Exception as e:
                        print("DB write error:", e)
                        client.send_response("register", 500, "Server DB Error")

                elif request["cmd"] == "login":
                    try:
                        DBManager.read("users")
                        client.send_response("login", 200, "Login was successful")
                    except Exception as e:
                        print("DB read error:", e)
                        client.send_response("login", 500, "Server DB Error")

                else:
                    client.send_response("error", 400, f"Unknown command: {request['cmd']}")

            except Exception as e:
                print("Error handling client:", e)
                client.send_response("error", 500, "Internal Server Error")
                break

        client.client_socket.close()
        print("Client connection closed")


if __name__ == '__main__':
    s = Server()
    s.run()