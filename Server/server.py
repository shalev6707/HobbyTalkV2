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
        """
        Handles client connection.
        :param client: the client to handle
        """
        print("Client connected")
        while True:
            try:
                request = client.get_request()
                if request is None:
                    print("Client disconnected or sent invalid data.")
                    break  # Safely exit the loop

                if "cmd" not in request or "data" not in request:
                    client.send_response("error", 400, "Invalid request format.")
                    continue

                if request["cmd"] == "register":
                    DBManager.write("users", request["data"])
                    client.send_response("register", 200, "Registration was successful")


                elif request["cmd"] == "login":

                    users = DBManager.read("users")

                    user = next((u for u in users if
                                 u["username"] == request["data"]["username"] and u["password"] == request["data"][
                                     "password"]), None)

                    if user:

                        client.send_response("login", 200, "Login was successful")

                    else:

                        client.send_response("login", 401, "Invalid username or password")


                else:
                    client.send_response("error", 400, f"Unknown command: {request['cmd']}")

            except Exception as e:
                print("Error handling client:", e)
                break

        client.client_socket.close()
        print("Client connection closed")


if __name__ == '__main__':
    s = Server()
    s.run()