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
        print(self.active_users)
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
                    username = request["data"]["username"]
                    password = request["data"]["password"]
                    bio = request["data"]["bio"]
                    hobbies = request["data"]["hobbies"]

                    data = DBManager.read("users.json")
                    if data is None:
                        data = {}  # Initialize if file is empty or missing

                    if username in data:
                        client.send_response("register", 409, "Username already exists.")
                    else:
                        data[username] = {
                            "username": username,
                            "password": password,
                            "bio": bio,
                            "hobbies": hobbies
                        }
                        DBManager.write("users.json", data)
                        client.send_response("register", 200, "Registration was successful.")


                elif request["cmd"] == "login":
                    username = request["data"]["username"]
                    password = request["data"]["password"]
                    users = DBManager.read("users.json")

                    if username in users and users[username]["password"] == password and username not in self.active_users:
                        client.send_response("login", 200, "Login successful")
                        self.active_users.append(username)
                        print(self.active_users)
                    else:
                        client.send_response("login", 401, "Invalid username or password")

                elif request["cmd"] == "matching":
                    username = request["data"]["username"]
                    users = DBManager.read("users.json")
                    active_users = self.active_users

                    if not users or username not in users:
                        client.send_response("matching", 404, "User not found")
                        return

                    user_hobbies = set(users[username]["hobbies"])
                    matches = []

                    for user, info in users.items():
                        if user == username or user not in active_users:
                            continue  # Skip self and offline users

                        common = user_hobbies.intersection(info["hobbies"])
                        match_score = len(common)
                        matches.append({
                            "username": user,
                            "score": match_score,
                            "bio": info.get("bio", "")
                        })

                    # Sort matches by score descending
                    matches.sort(key=lambda x: x["score"], reverse=True)
                    client.send_response("matching", 200, str(matches))


                elif request["cmd"] == "logout":
                    username = request["data"].get("username")
                    if username in self.active_users:
                        self.active_users.remove(username)
                        client.send_response("logout", 200, "Logout successful")
                        print(f"{username} removed from active users. Current: {self.active_users}")
                    else:
                        client.send_response("logout", 401, "User not found in active users")

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
