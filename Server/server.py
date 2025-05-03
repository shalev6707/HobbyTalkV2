from Server.DataBase.DatabaseManager import DBManager
from default import *
from Server.client_interface import ClientInterface

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080

        # Create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.active_users = []

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
        global username
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
                    DBManager.write("users", {request["data"]["username"]: request["data"]})
                    client.send_response("register", 200, "Registration was successful")

                # Handle 'login' command
                elif request["cmd"] == "login":
                    username = request["data"]["username"]
                    password = request["data"]["password"]
                    users = DBManager.read("users")

                    if username in users and users[username]["password"] == password:
                        client.send_response("login", 200, "Login successful")
                        self.active_users.append(username)
                    else:
                        client.send_response("login", 401, "Invalid username or password")
                elif request["cmd"] == "matching":
                    users = DBManager.read("users")
                    user_hobbies = users[request["data"]["username"]]["hobbies"]
                    matches = {}
                    for user in users:
                        matches[user] = 0
                        for hobby in users[user]["hobbies"]:
                            if hobby in user_hobbies[user]["hobbies"]:
                                matches[user] += 1
                    client.send_response("matching", 200, json.dumps(matches))
                elif request["cmd"] == "logout":
                    if username in self.active_users:
                        client.send_response("logout", 200, "Logout successful")
                        del self.active_users[username]



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