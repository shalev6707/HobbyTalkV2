# lobby_screen.py

import time
import socket
import threading
import tkinter as tk
from tkinter import messagebox
from Server.client_interface import ClientInterface
from Client import client
from base_screen import BaseScreen
import json
from encryptions import *
from vidstream import AudioSender, AudioReceiver


class LobbyScreen(BaseScreen):
    def __init__(self, master, app, client, username):
        super().__init__(master, title="Lobby", size="600x900")
        self.app = app
        self.client = client
        self.username = username
        self.matches = []
        self.caller_ip = None
        self.create_widgets()
        self.fetch_matches()

    def handle_call_accepted(self, response_data, port1, port2):
        """Start receiver, then safely attempt to start sender."""
        my_ip = socket.gethostbyname(socket.gethostname())
        receiver = AudioReceiver(my_ip, port1)
        sender = AudioSender(response_data.get("peer_ip"), port2)

        # Start listening thread
        threading.Thread(target=receiver.start_server, daemon=True).start()
        time.sleep(1)

        # Wrap sender in try/except to prevent thread crash on TimeoutError
        def _safe_send():
            try:
                sender.start_stream()
            except Exception as e:
                print("AudioSender error:", e)
                messagebox.showerror(
                    "Audio Error",
                    f"Could not connect to peer at {response_data.get('peer_ip')}:{port2}.\n"
                    "Please check that the other user accepted the call,\n"
                    "that IP/port are correct, and no firewall is blocking you."
                )

        threading.Thread(target=_safe_send, daemon=True).start()

    def create_widgets(self):
        tk.Label(self.frame, text=f"Welcome, {self.username}!", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.frame, text="Your Hobby Matches:", font=("Arial", 14)).pack()

        self.match_list = tk.Listbox(self.frame, width=40, selectmode=tk.SINGLE)
        self.match_list.pack(pady=10, padx=10, fill="both", expand=True)

        self.call_button = tk.Button(self.frame, text="Call", command=self.call)
        self.call_button.pack(pady=10)

        self.logout_button = tk.Button(self.frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=5)

    def fetch_matches(self):
        try:
            success, response_data = self.client.send_request("matching", {"username": self.username})
            if not success:
                messagebox.showerror("Error", "Failed to retrieve matches.")
                return

            # Populate matches
            self.match_list.delete(0, tk.END)
            self.matches = []
            for match in response_data.get("matches", []):
                text = f"{match['username']} - {match['score']} shared hobbies\nBio: {match['bio']}"
                self.match_list.insert(tk.END, text)
                self.matches.append(match["username"])

            # Handle incoming call request
            call_req = response_data.get("call_requests")
            if isinstance(call_req, dict):
                self.caller_ip = call_req.get("caller_ip")
                IncomingCallPopup(self.frame, call_req["caller_username"], self.on_accept, self.on_decline)

            # Poll again after 10s
            self.frame.after(10000, self.fetch_matches)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve matches: {e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.handle_logout(self.username)

    def call(self):
        """Initiate a call and start listening before the peer connects back."""
        if not self.match_list.curselection():
            return

        selected = self.matches[self.match_list.curselection()[0]]
        success, _ = self.client.send_request("call", {"username": selected})
        if not success:
            messagebox.showerror("Error", "Call failed.")
            return

        # Start receiver *before* the other side streams back
        my_ip = socket.gethostbyname(socket.gethostname())
        CALL_LISTEN_PORT = 1239  # must match callee's AudioSender port
        receiver = AudioReceiver(my_ip, CALL_LISTEN_PORT)
        threading.Thread(target=receiver.start_server, daemon=True).start()

    def on_accept(self, caller_username):
        success, response_data = self.client.send_request("accept_call", {"username": caller_username})
        if success:
            # After acceptance, connect out to the caller
            self.handle_call_accepted(response_data, 1238, 1239)

    def on_decline(self, caller_username):
        self.client.send_request("decline_call", {"username": caller_username})


class IncomingCallPopup(tk.Toplevel):
    def __init__(self, parent, caller_username, on_accept, on_decline):
        super().__init__(parent)
        self.title("Incoming Call")
        tk.Label(self, text=f"{caller_username} is calling you...").pack(padx=20, pady=10)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Accept",
                  command=lambda: self.respond(True, caller_username, on_accept),
                  bg="green", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Decline",
                  command=lambda: self.respond(False, caller_username, on_decline),
                  bg="red", fg="white").pack(side="left", padx=10)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.respond(False, caller_username, on_decline))

    def respond(self, accepted, caller_username, callback):
        self.destroy()
        callback(caller_username)
