from crocomine.client.crocomine_client import CrocomineClient
from Game import Game
import time

values_list = ["L", "W", "F", "T", "C", "S"]
values_dict = {
    "L": 1,
    "W": 2,
    "F": 3,
    "T": 4,
    "C": 5,
    "S": 6,
}

def test():
    m = 10
    n = 10
    game = Game(m, n, 0, 0, 0, 0, 0)
    print(game.get_adjacent_cells(0, 0))

def main():
    server = "http://localhost:8000"
    group = "Groupe 1"
    members = "Victor et Maxime"
    mine = CrocomineClient(server, group, members)

    ko_count = 0
    gg_count = 0
    fail = []

    end = True

    status, msg, grid_infos = mine.new_grid()
    map = msg
    start_time_grid = time.time()
    count = 1
    print(count)

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

    infos = []

    if status != 'GG' and status != 'Err':
        status, msg, infos = mine.discover(grid_infos['start'][0], grid_infos['start'][1])

    while end:
        print(status, msg, infos)
        if status == 'Err':
            end = False
        elif status == 'GG':
            gg_count += 1
            print()
            print("GRID --- %s seconds ---" % (time.time() - start_time_grid))
            status, msg, grid_infos = mine.new_grid()
            map = msg
            start_time_grid = time.time()
            count += 1
            print(count, 'GG')
            print()
            print(status, msg, infos)
            # end = False
            if end and status != 'Err':
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
            else:
                end = False
        elif status == 'KO':
            ko_count += 1
            fail.append(map)
            print()
            print("GRID --- %s seconds ---" % (time.time() - start_time_grid))
            status, msg, grid_infos = mine.new_grid()
            map = msg
            start_time_grid = time.time()
            count += 1
            print(count, 'KO')
            print()
            print(status, msg, infos)
            # end = False
            if end and status != 'Err':
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
            else:
                end = False
        elif status == 'OK':
            start_time = time.time()
            for cell in infos:
                game.add_information_constraints(cell)
            action, cell = game.make_decision()
            print("--- %s seconds ---" % (time.time() - start_time))
            print(action, cell)
            if action == 'guess':
                status, msg, infos = mine.guess(cell[0], cell[1], cell[2])
            elif action == 'discover':
                status, msg, infos = mine.discover(cell[0], cell[1])
            elif action == 'chord':
                status, msg, infos = mine.chord(cell[0], cell[1])
            else:
                ko_count += 1
                fail.append(map)
                print()
                print("GRID --- %s seconds ---" % (time.time() - start_time_grid))
                status, msg, grid_infos = mine.new_grid()
                map = msg
                start_time_grid = time.time()
                count += 1
                print(count, 'NONE')
                print()
                print(status, msg, infos)
                # end = False
                if end and status != 'Err':
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
                else:
                    end = False

    print('WIN:', gg_count)
    print('KO:', ko_count)
    print('FAILS', fail)
    print('Fin')


if __name__ == "__main__":
    main()