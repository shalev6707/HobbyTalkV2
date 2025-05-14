import tkinter as tk
from tkinter import messagebox
from base_screen import BaseScreen
import socket
from call__handler import CallHandler  # Correct import (single underscore)
from call_window import CallWindow

class LobbyScreen(BaseScreen):
    def __init__(self, master, app, client, username):
        super().__init__(master, title="Lobby", size="600x900")
        self.app = app
        self.client = client
        self.username = username
        self.call_active = False
        self.matches = []
        self.create_widgets()
        self.fetch_matches()

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
        if self.call_active:
            return  # Stop fetching if a call is in progress
        try:
            success, response_data = self.client.send_request("matching", {"username": self.username})
            if not success:
                messagebox.showerror("Error", "Failed to retrieve matches.")
                return

            match_data = response_data["matches"]
            self.match_list.delete(0, tk.END)
            self.matches = [match["username"] for match in match_data]
            for match in match_data:
                display_text = f"{match['username']} - {match['score']} shared hobbies\nBio: {match['bio']}"
                self.match_list.insert(tk.END, display_text)

            call_requests = response_data["call_requests"]
            for caller in call_requests:
                IncomingCallPopup(self.frame, caller, self.on_accept, self.on_decline)

            self.frame.after(5000, self.fetch_matches)  # Poll every 5 seconds

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve matches: {e}")

    def call(self):
        if self.call_active:
            return
        selected = self.match_list.curselection()
        if selected:
            target_username = self.matches[selected[0]]
            success, _ = self.client.send_request("call", {"username": target_username})
            if not success:
                messagebox.showerror("Error", "Call request failed.")

    def on_accept(self, peer_username):
        self.call_active = True
        self.client.send_request("accept_call", {"username": peer_username})
        self.launch_call(peer_username)

    def on_decline(self, peer_username):
        self.client.send_request("decline_call", {"username": peer_username})

    def launch_call(self, peer_username):
        self.master.destroy()
        call_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        call_socket.connect(("127.0.0.1", 8080))  # Change IP/port if needed
        handler = CallHandler(call_socket)
        handler.start_call()
        CallWindow(handler, self.username, peer_username)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.handle_logout(self.username)


class IncomingCallPopup(tk.Toplevel):
    def __init__(self, parent, caller_username, on_accept, on_decline):
        super().__init__(parent)
        self.title("Incoming Call")
        self.caller_username = caller_username

        tk.Label(self, text=f"{caller_username} is calling you...").pack(padx=20, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Accept", bg="green", fg="white",
                  command=lambda: self.respond(True, on_accept)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Decline", bg="red", fg="white",
                  command=lambda: self.respond(False, on_decline)).pack(side="left", padx=10)

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.respond(False, on_decline))

    def respond(self, accepted, callback):
        self.destroy()
        callback(self.caller_username)
