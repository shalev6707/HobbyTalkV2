import tkinter as tk

from Server.DataBase.DatabaseManager import DBManager
from base_screen import BaseScreen
from tkinter import messagebox
from Server import server


class LoginScreen(BaseScreen):
    def __init__(self, master, login_callback, go_to_register, client):
        super().__init__(master, title="Login", size="400x300")

        self.login_callback = login_callback
        self.go_to_register = go_to_register
        self.client = client
        self.master.title("Login")


        tk.Label(self.frame, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack(pady=5)

        tk.Label(self.frame, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.frame, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.frame, text="No account? Register", command=self.go_to_register, fg="blue", bd=0).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please enter both username and password")

        status, response = self.client.send_request("login", {"username": username, "password": password})
        if status:
            messagebox.showinfo("Success", "Login Successful")
            self.login_callback(username, password)

        else:
            messagebox.showerror("Error", "Login Failed")

