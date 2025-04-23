import tkinter as tk
from tkinter import messagebox
from base_screen import BaseScreen

HOBBIES = [
    "Music", "Sports", "Gaming", "Reading", "Cooking",
    "Traveling", "Photography", "Drawing", "Movies", "Fitness"
]

class RegisterScreen(BaseScreen):
    def __init__(self, master, register_callback, go_to_login):
        super().__init__(master, title="Register", size="400x650")

        self.register_callback = register_callback
        self.go_to_login = go_to_login
        self.selected_hobbies = []

        # Username
        tk.Label(self.frame, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(self.frame, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack(pady=5)

        # Bio
        tk.Label(self.frame, text="Bio").pack(pady=5)
        self.bio_entry = tk.Entry(self.frame)
        self.bio_entry.pack(pady=5)

        # Hobby Selection
        tk.Label(self.frame, text="Select 3 Hobbies").pack(pady=10)
        self.hobby_vars = {}

        for hobby in HOBBIES:
            var = tk.IntVar()
            cb = tk.Checkbutton(
                self.frame, text=hobby, variable=var,
                command=self.limit_hobby_selection
            )
            cb.pack(anchor='w')
            self.hobby_vars[hobby] = var

        # Register Button
        tk.Button(self.frame, text="Register", command=self.register_user).pack(pady=15)

        # Link to Login
        tk.Button(self.frame, text="Already have an account? Login", command=self.go_to_login, fg="blue", bd=0).pack()

    def limit_hobby_selection(self):
        selected = [hobby for hobby, var in self.hobby_vars.items() if var.get()]
        if len(selected) > 3:
            # Uncheck the most recently checked
            for hobby in selected:
                self.hobby_vars[hobby].set(0)
            messagebox.showwarning("Limit Exceeded", "You can select only 3 hobbies.")
        else:
            self.selected_hobbies = selected

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        bio = self.bio_entry.get()

        if not username or not password or not bio:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if len(self.selected_hobbies) != 3:
            messagebox.showerror("Error", "Please select exactly 3 hobbies.")
            return

        self.register_callback(username, password, bio, self.selected_hobbies)
