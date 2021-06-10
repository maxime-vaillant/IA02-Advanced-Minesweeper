from crocomine.client.crocomine_client import CrocomineClient
from Game import Game


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
        elif status == 'OK':
            for cell in infos:
                game.add_information_constraints(cell)
            game.make_decision()

            status, msg, grid_infos = mine.new_grid()
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

    print('Fin')


if __name__ == "__main__":
    main()