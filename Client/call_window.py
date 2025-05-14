import tkinter as tk

class CallWindow(tk.Toplevel):
    def __init__(self, handler, local_user, peer_user):
        super().__init__()
        self.handler = handler
        self.title("Voice Call")

        tk.Label(self, text=f"Voice call between {local_user} and {peer_user}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="End Call", command=self.end_call, bg="red", fg="white").pack(pady=20)

        self.protocol("WM_DELETE_WINDOW", self.end_call)

    def end_call(self):
        self.handler.stop_call()
        self.destroy()
