from Client.lobby_screen import LobbyScreen
from Server.DataBase.DatabaseManager import DBManager
from default import *

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("400x500")
        self.root.title("HobbyTalk")
        self.current_screen = None
        self.client = Client()
        self.show_login_screen()
        self.username = None


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
            go_to_register=self.show_register_screen,
            client=self.client
        )

    def show_register_screen(self):
        self.clear_screen()
        self.current_screen = RegisterScreen(
            master=self.root,
            register_callback=self.handle_register,
            go_to_login=self.show_login_screen
        )

    def show_lobby_screen(self, username):
        self.clear_screen()
        self.current_screen = LobbyScreen(
            master=self.root,
            app=self,
            client=self.client,
            username=username  # ← required by your LobbyScreen
        )

    def handle_register(self, username, password, bio, hobbies):
        print("Register clicked!")
        print("Username:", username)
        print("Password:", password)
        print("Bio:", bio)
        print("Hobbies:", hobbies)
        status = self.client.send_request("register", {"username": username, "password": password, "bio": bio, "hobbies": hobbies})
        if status:
            messagebox.showinfo("Register Completed Successfully", "The user have been created.")
            self.show_login_screen()

    def handle_login(self, username, password):
        print("Login clicked!")
        status = self.client.send_request("login", {"username": username, "password": password})

        if status:
            self.username = username
            self.show_lobby_screen(self.username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_logout(self,username):
        print("Logout clicked!")
        users = DBManager.read("users.json")
        status = self.client.send_request("logout", {"username": username})
        if status:
            print("Logout successful!!")
            self.username = None
            self.clear_screen()
            self.show_login_screen()
            messagebox.showinfo("Logout", "Logout successful!")


if __name__ == '__main__':
    app = App()
    app.run()