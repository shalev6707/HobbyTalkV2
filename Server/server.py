# server.py

import socket
import threading
import json
import hashlib

# Adjust this if your DatabaseManager.py lives somewhere else:
from DataBase.DatabaseManager import DBManager
# Likewise, if client_interface.py is in the same folder:
from client_interface import ClientInterface


class Server:
    def __init__(self):
        self.host = "192.168.1.144"
        self.port = 8080
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

        self.active_users = []
        # receiver_username -> { "caller_username": ..., "caller_ip": ... }
        self.call_requests = {}
        # username -> ClientInterface
        self.connected_clients = {}

    def run(self):
        print(f"Server listening on {self.host}:{self.port}")
        self.socket.listen()
        while True:
            sock, addr = self.socket.accept()
            client = ClientInterface(sock, addr)
            threading.Thread(
                target=self.handle_client,
                args=(client,),
                daemon=True
            ).start()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def handle_client(self, client: ClientInterface):
        print("Client connected", client.client_addr)
        while True:
            request = client.get_request()
            if not request:
                break

            cmd = request.get("cmd")
            data = request.get("data", {})

            if cmd == "register":
                username = data.get("username")
                users = DBManager.read("users.json") or {}
                if username in users:
                    client.send_response("register", 409, "Username already exists.")
                else:
                    users[username] = {
                        "username": username,
                        "password": self.hash_password(data.get("password", "")),
                        "bio": data.get("bio", ""),
                        "hobbies": data.get("hobbies", [])
                    }
                    DBManager.write("users.json", users)
                    client.send_response("register", 200, "Registration successful.")

            elif cmd == "login":
                username = data.get("username")
                users = DBManager.read("users.json") or {}
                if (username in users and
                    users[username]["password"] == self.hash_password(data.get("password", "")) and
                    username not in self.active_users):
                    client.send_response("login", 200, "Login successful.")
                    self.active_users.append(username)
                    self.connected_clients[username] = client
                    client.username = username
                else:
                    client.send_response("login", 401, "Invalid credentials.")

            elif cmd == "matching":
                username = data.get("username")
                users = DBManager.read("users.json") or {}
                if username not in users:
                    client.send_response("matching", 404, "User not found.")
                else:
                    # compute matches...
                    user_hobbies = set(users[username]["hobbies"])
                    matches = []
                    for u, info in users.items():
                        if u == username or u not in self.active_users:
                            continue
                        common = user_hobbies.intersection(info["hobbies"])
                        matches.append({
                            "username": u,
                            "score": len(common),
                            "bio": info.get("bio", "")
                        })
                    matches.sort(key=lambda x: x["score"], reverse=True)
                    # pull any pending call
                    call_req = self.call_requests.pop(username, None)
                    client.send_response(
                        "matching", 200, "Matching retrieved.",
                        {"matches": matches, "call_requests": call_req}
                    )

            elif cmd == "call":
                receiver = data.get("username")
                caller = client.username
                caller_ip = client.client_addr[0]
                if receiver not in self.active_users:
                    client.send_response("call", 404, "User not online.")
                else:
                    self.call_requests[receiver] = {
                        "caller_username": caller,
                        "caller_ip": caller_ip
                    }
                    client.send_response("call", 200, "Call initiated.")

            elif cmd == "accept_call":
                caller = data.get("username")
                caller_client = self.connected_clients.get(caller)
                if caller_client:
                    # exchange IPs
                    caller_ip = caller_client.client_addr[0]
                    recv_ip = client.client_addr[0]
                    caller_client.send_response(
                        "call_accepted", 200, "Call accepted.",
                        {"peer_ip": recv_ip}
                    )
                    client.send_response(
                        "call_accepted", 200, "Call accepted.",
                        {"peer_ip": caller_ip}
                    )
                else:
                    client.send_response("accept_call", 404, "Caller not connected.")

            elif cmd == "decline_call":
                caller = data.get("username")
                caller_client = self.connected_clients.get(caller)
                if caller_client:
                    caller_client.send_response("call_declined", 200, "Call declined.")
                client.send_response("decline_call", 200, "You declined the call.")

            elif cmd == "logout":
                user = data.get("username")
                if user in self.active_users:
                    self.active_users.remove(user)
                    client.send_response("logout", 200, "Logout successful.")
                else:
                    client.send_response("logout", 401, "User not active.")

            else:
                client.send_response("error", 400, f"Unknown command: {cmd}")

        client.client_socket.close()
        print(f"Connection closed: {client.client_addr}")


if __name__ == "__main__":
    Server().run()
