from Game.game import Pong
from Menu.menu import Menu

if __name__ == "__main__":
    # Menu
    menu = Menu()
    local_client, client = menu.run()

    # Game
    game = Pong("Bob", local_client, client)
    game.run()
    game.quit()