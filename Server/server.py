from Server.DataBase.DatabaseManager import DBManager
from default import *
from Server.client_interface import ClientInterface
import hashlib
from vidstream import *

from encryptions import *


class Server:
    def __init__(self):
        self.host = "192.168.1.125"
        self.port = 8080

        # Create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))


        self.active_users = []
        self.call_requests = {}
        self.connected_clients = {}

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


    def hash_password(self,password):
        return hashlib.sha256(password.encode()).hexdigest()


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
                            "password": self.hash_password(password),
                            "bio": bio,
                            "hobbies": hobbies
                        }
                        DBManager.write("users.json", data)
                        client.send_response("register", 200, "Registration was successful.")


                elif request["cmd"] == "login":
                    username = request["data"]["username"]
                    password = request["data"]["password"]
                    users = DBManager.read("users.json")

                    if username in users and users[username]["password"] ==self.hash_password(password) and username not in self.active_users:
                        client.send_response("login", 200, "Login successful")
                        self.active_users.append(username)
                        self.connected_clients[username] = client
                        client.username = username
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
                    client.send_response("matching", 200, "matching successful",{"matches": matches, "call_requests": (self.call_requests[username] if username in self.call_requests else [])})

                elif request["cmd"] == "call":
                    receiver = request["data"]["username"]
                    caller_ip = client.client_addr[0]
                    print(receiver)
                    if receiver not in self.active_users:
                        client.send_response("matching", 404, "User not found")
                        return

                    self.call_requests[receiver] = (client.username, caller_ip)[0]
                    client.send_response("call", 200, "Call was successful")

                elif request["cmd"] == "accept_call":
                    caller_username = request["data"]["username"]
                    receiver_username = client.username

                    caller_client = self.connected_clients[caller_username]
                    receiver_client = self.connected_clients[receiver_username]

                    caller_ip = caller_client.client_addr[0]
                    receiver_ip = receiver_client.client_addr[0]

                    print(caller_ip)
                    print(receiver_ip)

                    # Notify both clients with each other's IP
                    caller_client.send_response("call_accepted", 200, "Call accepted", {
                        "peer_ip": receiver_ip,
                        "peer_username": receiver_username
                    })

                    receiver_client.send_response("call_accepted", 200, "Call accepted", {
                        "peer_ip": caller_ip,
                        "peer_username": caller_username
                    })

                    print(receiver_ip)
                    print(caller_ip)

                    self.call_requests = []

                elif request["cmd"] == "decline_call":
                    caller_username = request["data"]["username"]
                    caller_client = self.connected_clients.get(caller_username)

                    if caller_client:
                        caller_client.send_response("call_declined", 200, "Call declined")

                    client.send_response("call_declined", 200, "Call declined")

                    self.call_requests = []





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
