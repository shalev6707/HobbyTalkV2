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
        Handles communication with a connected client.

        :param client: The client to handle.
        """
        print("Client connected")
        while True:
            try:
                # Receive the request from client
                request = client.get_request()
                if request is None:
                    print("Client disconnected or sent invalid data.")
                    break  # Exit the loop safely

                # Check if request is valid
                if "cmd" not in request or "data" not in request:
                    client.send_response("error", 400, "Invalid request format.")
                    continue

                # Handle 'register' command
                if request["cmd"] == "register":
                    DBManager.write("users", request["data"])
                    client.send_response("register", 200, "Registration was successful")

                # Handle 'login' command
                elif request["cmd"] == "login":
                    try:
                        users = DBManager.read("users")  # Read all users from the database
                        username = request["data"]["username"]
                        password = request["data"]["password"]

                        # Find a user that matches both username and password
                        matching_user = next(
                            (user for user in users if user["username"] == username and user["password"] == password),
                            None
                        )

                        if matching_user:
                            client.send_response("login", 200, "Login was successful")
                        else:
                            client.send_response("login", 401, "Invalid username or password")

                    except Exception as e:
                        print("DB read error:", e)
                        client.send_response("login", 500, "Server DB Error")

                # Handle 'get_users' command (optional)
                elif request["cmd"] == "get_users":
                    try:
                        users = DBManager.read("users")
                        client.send_response("get_users", 200, users)
                    except Exception as e:
                        print("DB read error:", e)
                        client.send_response("get_users", 500, "Server DB Error")

                # Unknown command
                else:
                    client.send_response("error", 400, f"Unknown command: {request['cmd']}")

            except Exception as e:
                print("Error handling client:", e)
                break

        # Close client socket when done
        client.client_socket.close()
        print("Client connection closed")


if __name__ == '__main__':
    s = Server()
    s.run()