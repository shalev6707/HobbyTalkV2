import tkinter as tk

class BaseScreen:
    """
    A base screen class to simplify the creation of different GUI screens.
    Includes a master window, a main frame, and window configuration.
    """

    def __init__(self, master: tk.Tk, title: str = "HobbyTalk", size: str = "400x400"):
        self.master = master
        self.master.title(title)
        self.master.geometry(size)
        self.master.resizable(False, False)

        # Main frame to pack widgets into
        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.frame.pack(expand=True)

    def clear_frame(self):
        """
        Destroys all widgets in the main frame.
        Useful for switching views.
        """
        for widget in self.frame.winfo_children():
            widget.destroy()
