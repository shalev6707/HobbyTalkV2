from Client.base_screen import BaseScreen
from Client.lobby_screen import LobbyScreen
from Server.DataBase.DatabaseManager import DBManager
from default import *
from app import App


if __name__ == '__main__':
    app = App()
    app.run()