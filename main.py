from crocomine.client.crocomine_client import CrocomineClient
from Game import Game

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
    for i in range(m):
        for j in range(n):
            for key in values_dict:
                var = game.cell_to_variable(i, j, key)
                cell = game.variable_to_cell(var)
                if i != cell[0] or j != cell[1] or key != cell[2]:
                    print(var, cell, (i, j, key))

def main():
    server = "http://localhost:8000"
    group = "Groupe 1"
    members = "Victor et Maxime"
    mine = CrocomineClient(server, group, members)

    end = True

    status, msg, grid_infos = mine.new_grid()

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
        elif status == 'GG' or status == 'KO':
            status, msg, grid_infos = mine.new_grid()
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
            else:
                end = False
        elif status == 'OK':
            for cell in infos:
                game.add_information_constraints(cell)
            action, cell = game.make_decision()
            print(action, cell)
            if action == 'guess':
                status, msg, infos = mine.guess(cell[0], cell[1], cell[2])
            elif action == 'discover':
                status, msg, infos = mine.discover(cell[0], cell[1])
            else:
                end = False

    print('Fin')


if __name__ == "__main__":
    main()