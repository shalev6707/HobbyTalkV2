import tkinter as tk
from tkinter import messagebox
from base_screen import BaseScreen

class LobbyScreen(BaseScreen):
    def __init__(self, master, app, client, username):
        super().__init__(master, title="Lobby", size="600x900")
        self.app = app
        self.client = client
        self.username = username
        self.match_list = None
        self.logout_button = None

        self.create_widgets()
        self.fetch_matches()

    def create_widgets(self):
        tk.Label(self.frame, text=f"Welcome, {self.username}!", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.frame, text="Your Hobby Matches:", font=("Arial", 14)).pack()

        self.match_list = tk.Listbox(self.frame, width=40)
        self.match_list.pack(pady=10, padx=10, fill="both", expand=True)

        self.logout_button = tk.Button(self.frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=5)

    def fetch_matches(self):
        response = self.client.send_request("matching", {"username": self.username})
        if isinstance(response, dict):
            sorted_matches = sorted(response.items(), key=lambda x: x[1], reverse=True)
            for user, score in sorted_matches:
                if user != self.username:
                    self.match_list.insert(tk.END, f"{user} - {score} shared hobbies")
        else:
            messagebox.showerror("Error", "Failed to retrieve matches.")

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.app.handle_logout(self.username)

