from http.client import responses

from default import *

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("400x500")
        self.root.title("HobbyTalk")
        self.current_screen = None
        self.show_login_screen()
        self.client = Client()

    def run(self):
        self.root.mainloop()

    def clear_screen(self):
        if self.current_screen:
            self.current_screen.frame.destroy()
            self.current_screen = None

    def show_login_screen(self):
        self.clear_screen()
        self.current_screen = LoginScreen(
            master=self.root,
            login_callback=self.handle_login,
            go_to_register=self.show_register_screen
        )

    def show_register_screen(self):
        self.clear_screen()
        self.current_screen = RegisterScreen(
            master=self.root,
            register_callback=self.handle_register,
            go_to_login=self.show_login_screen
        )

    def handle_register(self, username, password, bio, hobbies):
        print("Register clicked!")
        print("Username:", username)
        print("Password:", password)
        print("Bio:", bio)
        print("Hobbies:", hobbies)
        status = self.client.send_request("register", {"username": username, "password": password, "bio": bio, "hobbies": hobbies})
        if status:
            self.show_login_screen()
            messagebox.showinfo("Register Completed Successfully", "The user have been created.")


    def handle_login(self, username, password):
        print("Login clicked!")
        print("Username:", username)
        print("Password:", password)
        status = self.client.send_request("login", {"username": username, "password": password})
        messagebox.showinfo("Login", "Login successful!")
        # self.show_lobby_screen(username)  # Placeholder


if __name__ == '__main__':
    app = App()
    app.run()