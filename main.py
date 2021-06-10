from crocomine.client.crocomine_client import CrocomineClient

from Game import Game

def api():
    server = "http://localhost:8000"
    group = "Groupe 1"
    members = "Victor et Maxime"
    mine = CrocomineClient(server, group, members)

def main():
    # TODO Get first values from the api

    status, msg, infos = croco.new(0, 0)

    game = Game(4, 4)

    print(game.exec_gophersat())

    end = False


if __name__ == "__main__":
    main()