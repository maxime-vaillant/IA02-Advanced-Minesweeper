import time
from typing import Tuple

from Game import Game
from crocomine.client.crocomine_client import CrocomineClient


def create_new_grid(mine: CrocomineClient) -> Tuple[bool, Tuple]:
    status, msg_map, grid_infos = mine.new_grid()
    if status != 'Err':
        game = Game(
            grid_infos['m'],
            grid_infos['n'],
            grid_infos['tiger_count'],
            grid_infos['shark_count'],
            grid_infos['croco_count'],
            grid_infos['land_count'],
            grid_infos['sea_count']
        )
        status, msg, infos = mine.discover(grid_infos['start'][0], grid_infos['start'][1])
        return True, (game, status, msg, infos, msg_map)
    return False, ()


def main():
    server = "http://localhost:8000"
    group = "Group 1"
    members = "Victor et Maxime"
    mine = CrocomineClient(server, group, members)

    DISPLAY = True

    total_time = 0
    total_move = 0

    ko_count = 0
    gg_count = 0
    fail = []

    count = 0
    nb_move = 0

    new_grid = create_new_grid(mine)

    start_time_grid = time.time()

    end = new_grid[0]

    if end:
        game, status, msg, infos, msg_map = new_grid[1]

        while end:
            if DISPLAY:
                print(status, msg, infos)
            if status == 'Err':
                # TODO: Check errors
                end = False
            elif status == 'GG':
                if DISPLAY:
                    print()
                    print("GG")
                    print("GRID --- %s seconds ---" % (time.time() - start_time_grid))
                    print("Nombre de coup", nb_move)
                    print()

                total_time += time.time() - start_time_grid
                total_move += nb_move
                gg_count += 1

                new_grid = create_new_grid(mine)

                end = new_grid[0]

                if end:
                    game, status, msg, infos, msg_map = new_grid[1]

                    nb_move = 0
                    start_time_grid = time.time()
                    count += 1

                    if DISPLAY:
                        print(count)
                        print()
            elif status == 'KO':
                if DISPLAY:
                    print()
                    print("KO")
                    print("GRID --- %s seconds ---" % (time.time() - start_time_grid))
                    print("Nombre de coup", nb_move)
                    print()

                total_time += time.time() - start_time_grid
                total_move += nb_move
                ko_count += 1
                fail.append(msg_map)

                new_grid = create_new_grid(mine)

                end = new_grid[0]

                if end:
                    game, status, msg, infos, msg_map = new_grid[1]

                    nb_move = 0
                    start_time_grid = time.time()
                    count += 1

                    if DISPLAY:
                        print(count)
                        print()
            elif status == 'OK':
                nb_move += 1
                start_time = time.time()

                for cell in infos:
                    game.add_information_constraints(cell)
                action, cell = game.make_decision()

                if DISPLAY:
                    print("DECISION --- %s seconds ---" % (time.time() - start_time))
                    print(action, cell)

                if action == 'guess':
                    status, msg, infos = mine.guess(cell[0], cell[1], cell[2])
                elif action == 'discover':
                    status, msg, infos = mine.discover(cell[0], cell[1])
                elif action == 'chord':
                    status, msg, infos = mine.chord(cell[0], cell[1])
                else:
                    if DISPLAY:
                        print("NONE")
                    status = "KO"

    print('WIN:', gg_count)
    print('KO:', ko_count)
    print('FAILS', fail)
    print()
    print("TEMPS TOTAL", total_time)
    print("NOMBRE COUP TOTAL", total_move)
    print('Fin')


if __name__ == "__main__":
    main()
