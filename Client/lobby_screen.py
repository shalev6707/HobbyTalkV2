import tkinter as tk
from tkinter import messagebox
from Server.client_interface import ClientInterface
from Client import client
from base_screen import BaseScreen
import json
from encryptions import *


class LobbyScreen(BaseScreen):
    def __init__(self, master, app, client, username):
        super().__init__(master, title="Lobby", size="600x900")
        self.app = app
        self.client = client
        self.username = username
        self.match_list = None
        self.logout_button = None
        self.matches = []
        self.create_widgets()
        self.fetch_matches()




    def create_widgets(self):
        tk.Label(self.frame, text=f"Welcome, {self.username}!", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.frame, text="Your Hobby Matches:", font=("Arial", 14)).pack()

        self.match_list = tk.Listbox(self.frame, width=40,selectmode=tk.SINGLE)
        self.match_list.pack(pady=10, padx=10, fill="both", expand=True)

        self.call_button = tk.Button(self.frame, text="Call", command=self.call)
        self.call_button.pack(pady=10)

        self.logout_button = tk.Button(self.frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=5)




    def fetch_matches(self):
        try:
            success, response_data = self.client.send_request("matching", {"username": self.username})
            print(response_data)
            if not success:
                messagebox.showerror("Error", "Failed to retrieve matches.")
                return
            try:
                if response_data["cmd"] == "call_accepted":
                    self.app.handle_call_accepted(response_data)
            except:
                pass

            # Now decode the match data (which should still be a JSON string)
            match_data = response_data["matches"]

            self.match_list.delete(0, tk.END)
            self.matches = [match["username"] for match in match_data]
            for match in match_data:
                display_text = f"{match['username']} - {match['score']} shared hobbies\nBio: {match['bio']}"
                self.match_list.insert(tk.END, display_text)

            username = response_data["call_requests"]

            if type(username) == str:
                print(username)
                IncomingCallPopup(self.frame, username, self.on_accept, self.on_decline)
            self.frame.after(10000, self.fetch_matches)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve matches: {e}")

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.app.handle_logout(self.username)

    def call(self):
        if len(self.match_list.curselection()) > 0:
            selected_username = self.matches[self.match_list.curselection()[0]]
            success, response_data = self.client.send_request("call", {"username": selected_username})
            if not success:
                messagebox.showerror("Error", "call failed")




    def on_accept(self, username):
        response = self.client.send_request("accept_call", {"username": username})
        self.app.handle_call_accepted(response)

    def on_decline(self, username):
        self.client.send_request("decline_call", {"username": username})



class IncomingCallPopup(tk.Toplevel):
    def __init__(self, parent, caller_username, on_accept, on_decline):
        super().__init__(parent)
        self.title("Incoming Call")
        self.caller_username = caller_username

        self.label = tk.Label(self, text=f"{caller_username} is calling you...")
        self.label.pack(padx=20, pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        accept_btn = tk.Button(button_frame, text="Accept", bg="green", fg="white",
                               command=lambda: self.respond(True, on_accept))
        accept_btn.pack(side="left", padx=10)

        decline_btn = tk.Button(button_frame, text="Decline", bg="red", fg="white",
                                command=lambda: self.respond(False, on_decline))
        decline_btn.pack(side="left", padx=10)

        # Prevent interaction with other windows
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.respond(False, on_decline))

    def respond(self, accepted, callback):
        self.destroy()
        callback(self.caller_username)




