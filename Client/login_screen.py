import tkinter as tk
from base_screen import BaseScreen
from tkinter import messagebox

class LoginScreen(BaseScreen):
    def __init__(self, master, login_callback, go_to_register):
        super().__init__(master, title="Login", size="400x300")

        self.login_callback = login_callback
        self.go_to_register = go_to_register

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

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            self.login_callback(username, password)
