import itertools
from math import comb
from typing import List, Tuple, Dict
import pycryptosat as pysat
import random

# F: Free, T: Tiger, S: Shark, C: Crocodile
values_list = ["F", "T", "S", "C"]
values_dict = {
    "F": 1,
    "T": 2,
    "S": 3,
    "C": 4,
}
animals = ("T", "S", "C")
length = len(values_dict)


class Game:
    """
    This class represents a game board
    """

    def __init__(self, height: int, width: int, tiger_count: int, shark_count: int, crocodile_count: int,
                 land_count: int, sea_count: int):
        """
        Default constructor
        """
        self.solver = pysat.Solver()
        self.width = width
        self.height = height
        self.board = [
            [{
                'type': '?',
                'field': '?',
                'prox_count': [],
                'known_count': {
                    'T': 0,
                    'S': 0,
                    'C': 0,
                    'F': 0
                },
                'near_cells': self.get_near_cells(i, j)
            } for j in range(width)] for i in range(height)
        ]
        self.infos = {
            "T": {
                "guess": 0,
                "count": tiger_count
            },
            "S": {
                "guess": 0,
                "count": shark_count
            },
            "C": {
                "guess": 0,
                "count": crocodile_count
            },
            "land": {
                "found": 0,
                "count": land_count
            },
            "sea": {
                "found": 0,
                "count": sea_count
            }
        }
        self.visitedCells = []
        self.guest_moves = []
        self.response = []
        self.last_cells_visited = []
        self.refresh_guess = True

    def cell_to_variable(self, i: int, j: int, val: str) -> int:
        """
        Transform a cell representation to a variable
        :param i: 0 <= i < self.height
        :param j: 0 <= j < self.width
        :param val: val in ['F', 'T', 'S', 'C']
        :return variable
        """
        return i * self.width * length + j * length + values_dict[val]

    def variable_to_cell(self, var: int) -> Tuple[int, int, str]:
        """
        Change a variable to his cell value
        :param var: variable
        :return cell
        """
        var -= 1
        i, rest = var // (self.width * length), var % (self.width * length)
        j = rest // length
        val = values_list[(var + 1) % length - 1]
        return i, j, val

    @staticmethod
    def at_least_one(vars: List[int]) -> List[int]:
        return vars[:]

    def exact(self, vars: List[int], param: int) -> List[List[int]]:
        """
        :param param: number exact
        :param vars: in clauses list
        :return: list of exact number clauses
        """
        clauses = [self.at_least_one(vars)] if param != 0 or param == len(vars) else []
        clauses += [[x] for x in vars] if param == len(vars) else []
        for combination in itertools.combinations([-x for x in vars[:]], param + 1):
            clause = []
            for i in range(param + 1):
                clause.append(combination[i])
            clauses.append(clause)
        return clauses

    def get_near_cells(self, i: int, j: int) -> List[List[int]]:
        """
        :param i: 0 <= i < self.height
        :param j: 0 <= j < self.width
        :return: List of position of near cells
        """
        cells = []
        for a in range(i - 1, i + 2):
            for b in range(j - 1, j + 2):
                if 0 <= a < self.height and 0 <= b < self.width and (a != i or b != j):
                    cells.append([a, b])
        return cells

    def get_adjacent_cells(self, i: int, j: int) -> List[List[int]]:
        """
        :param i: 0 <= i < self.height
        :param j: 0 <= j < self.width
        :return: List of position of adjacent cells
        """
        cells = []
        for a in range(i - 1, i + 2):
            for b in range(j - 1, j + 2):
                if 0 <= a < self.height and 0 <= b < self.width and ((a != i and b == j) or (a == i and b != j)):
                    cells.append([a, b])
        return cells

    def create_rule_on_cell(self, i: int, j: int) -> List[List[int]]:
        """
        :param i: 0 <= i < self.height
        :param j: 0 <= j < self.width
        :return: rules clauses
        """
        cells = []
        for key in values_dict:
            cells.append(self.cell_to_variable(i, j, key))
        return self.exact(cells, 1)

    def create_rule_animal_remaining(self, animal: str, param: int) -> List[List[int]]:
        """
        :param animal: animal in ['T', 'S', 'C']
        :param param: Number remaining
        :return: clauses
        """
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j]['type'] == '?':
                    cells.append(self.cell_to_variable(i, j, animal))
        return self.exact(cells, param)

    def filter_discover(self, item) -> bool:
        i, j = item
        cell = self.board[i][j]
        return cell['prox_count'] and sum(cell['known_count'].values()) != len(cell['near_cells'])

    def filter_chord(self, item) -> bool:
        i, j = item
        cell = self.board[i][j]
        return cell['prox_count'] and sum(cell['prox_count']) == sum(cell['known_count'].values()) - cell['known_count']['F'] and sum(cell['known_count'].values()) != len(cell['near_cells'])

    def filter_guess(self, item) -> bool:
        i, j = item
        cell = self.board[i][j]
        return cell['type'] == '?' and cell['field'] != '?'

    def make_guess_move(self) -> Tuple[bool, Tuple]:
        if len(self.guest_moves) > 0:
            return True, self.guest_moves.pop(0)
        if self.refresh_guess:
            self.refresh_guess = False
            for var in range(1, self.height*self.width*length+1):
                cell = self.variable_to_cell(var)
                if [cell[0], cell[1]] in self.last_cells_visited and cell[2] != 'F' and self.board[cell[0]][cell[1]]['type'] == '?':
                    # Try to deduct with UNSAT
                    deduction = self.solver.solve([-var])
                    if not deduction[0]:
                        self.guest_moves.append(cell)
            self.last_cells_visited.clear()
            if len(self.guest_moves) > 0:
                return True, self.guest_moves.pop(0)
        return False, ()

    def make_chord_move(self) -> Tuple[bool, Tuple]:
        chord_moves = list(filter(self.filter_chord, self.visitedCells))
        chord_moves.sort(key=lambda x: sum(self.board[x[0]][x[1]]['known_count'].values()) - len(self.board[x[0]][x[1]]['near_cells']))
        if len(chord_moves) > 0:
            self.refresh_guess = True
            return True, chord_moves[0]
        return False, ()

    def make_discover_move(self) -> Tuple[bool, Tuple]:
        for var in range(1, self.height*self.width*length+1):
            if var > 0:
                cell = self.variable_to_cell(var)
                if cell[2] == 'F' and self.board[cell[0]][cell[1]]['type'] == '?':
                    # Try to deduct with UNSAT
                    deduction = self.solver.solve([-var])
                    if not deduction[0]:
                        return True, cell
        return False, ()

    def make_random_move_bis(self) -> Tuple[bool, Tuple]:
        probability, moves = [], []
        total_animal_found, total_animal = 0, 0
        probability_infos = []
        all_near_cells_unknown = []
        for key in self.infos:
            if key in animals:
                total_animal_found += self.infos[key]['guess']
                total_animal += self.infos[key]['count']
        for v in filter(self.filter_discover, self.visitedCells):
            cell = self.board[v[0]][v[1]]
            field_count = {
                'sea': 0,
                'land': 0
            }
            t = cell['prox_count'][0] - cell['known_count']['T']
            s = cell['prox_count'][1] - cell['known_count']['S']
            c = cell['prox_count'][2] - cell['known_count']['C']
            unknown_count = len(cell['near_cells']) - sum(cell['known_count'].values())
            near_cells_unknown = []
            for (i, j) in cell['near_cells']:
                if self.board[i][j]['type'] == '?':
                    near_cells_unknown.append((i, j))
                    if (i, j) not in all_near_cells_unknown:
                        all_near_cells_unknown.append((i, j))
                    field = self.board[i][j]['field']
                    field_count[field] += 1
            probability_infos.append({
                'pos': c,
                'prox': t + s + c,
                'near_cells_unknown': near_cells_unknown,
                'sea_probability': s / field_count['sea'] + c / (unknown_count - s),
                'land_probability': t / field_count['land'] + c / (unknown_count - t)
            })
            for cell in all_near_cells_unknown:
                probability = 0
                for p in probability_infos:
                    if cell in p['near_cells_unknown']:
                        probability = max(p['sea_probability'] if self.board[cell[0]][cell[1]]['field'] == 'sea' else p['land_probability'], probability)

    def make_random_move(self) -> Tuple[bool, Tuple]:
        probability, moves = [], []
        total_animal_found, total_animal = 0, 0
        for key in self.infos:
            if key in animals:
                total_animal_found += self.infos[key]['guess']
                total_animal += self.infos[key]['count']
        for c in filter(self.filter_discover, self.visitedCells):
            cell = self.board[c[0]][c[1]]
            field_count = {
                'sea': 0,
                'land': 0
            }
            t = cell['prox_count'][0] - cell['known_count']['T']
            s = cell['prox_count'][1] - cell['known_count']['S']
            c = cell['prox_count'][2] - cell['known_count']['C']
            unknown_count = len(cell['near_cells']) - sum(cell['known_count'].values())
            for (i, j) in cell['near_cells']:
                if self.board[i][j]['type'] == '?':
                    field = self.board[i][j]['field']
                    field_count[field] += 1
            for (i, j) in cell['near_cells']:
                if self.board[i][j]['type'] == '?':
                    if self.board[i][j]['field'] == 'sea':
                        prob = s / field_count['sea'] + c / (unknown_count - s)
                        probability.append([i, j, prob])
                    else:
                        prob = t / field_count['land'] + c / (unknown_count - t)
                        probability.append([i, j, prob])
        known = []
        for i in range(len(probability)):
            for j in range(i+1, len(probability)):
                if probability[i][0] == probability[j][0] and probability[i][1] == probability[j][1]:
                    if probability[i][2] > probability[j][2]:
                        probability[j][2] = probability[i][2]
                    else:
                        probability[i][2] = probability[j][2]
            if (probability[i][0], probability[i][1], probability[i][2]) not in known:
                known.append((probability[i][0], probability[i][1], probability[i][2]))
        known.sort(key=lambda x: x[2])
        unknown = []
        for i in range(self.height):
            for j in range(self.width):
                if [i, j] not in self.visitedCells:
                    unknown.append((i, j))
        unknown_probability = 1 if len(unknown) == 0 else (total_animal - total_animal_found) / len(unknown)
        if len(probability) > 0:
            if probability[0][2] < unknown_probability:
                for p in probability:
                    if p[2] == probability[0][2]:
                        moves.append(p)
                return True, random.choice(moves)
        return True, random.choice(unknown)

    def add_information_constraints(self, data: Dict):
        i, j = data['pos']
        field = data['field']
        self.board[i][j]['field'] = field
        proximity_count = data.get('prox_count', None)
        guess_animal = data.get('animal', None)
        if guess_animal:
            # Increment guess count
            self.infos[guess_animal]['guess'] += 1
            # Add the guess on the board
            self.board[i][j]['type'] = guess_animal
            for cell in self.board[i][j]['near_cells']:
                self.board[cell[0]][cell[1]]['known_count'][guess_animal] += 1
        elif proximity_count:
            if [i, j] not in self.visitedCells:
                self.visitedCells.append([i, j])
                self.solver.add_clause([-self.cell_to_variable(i, j, "T") if field == "sea" else -self.cell_to_variable(i, j, "S")])
            # Increment field count if new cell discovered
            self.infos[field]['found'] += 1
            self.board[i][j]['type'] = 'F'
            self.board[i][j]['prox_count'] = proximity_count
            self.solver.add_clause([self.cell_to_variable(i, j, 'F')])
            near_cells = self.board[i][j]['near_cells']
            for cell in near_cells:
                self.last_cells_visited.append(cell)
                self.board[cell[0]][cell[1]]['known_count']['F'] += 1
                if cell not in self.visitedCells:
                    self.visitedCells.insert(0, cell)
                    self.solver.add_clauses(self.create_rule_on_cell(cell[0], cell[1]))
            total_count = 0
            for index, count in enumerate(proximity_count):
                total_count += count
                cells = []
                animal = animals[index]
                for cell in near_cells:
                    cells.append(self.cell_to_variable(cell[0], cell[1], animal))
                self.solver.add_clauses(self.exact(cells, count))
            cells = []
            for cell in near_cells:
                cells.append(self.cell_to_variable(cell[0], cell[1], "F"))
            self.solver.add_clauses(self.exact(cells, len(near_cells) - total_count))
        else:
            self.solver.add_clause([-self.cell_to_variable(i, j, "T") if field == "sea" else -self.cell_to_variable(i, j, "S")])

    def make_decision(self) -> Tuple[str, Tuple]:
        if self.height * self.width > 5000:
            chord = self.make_chord_move()
            if chord[0]:
                return 'chord', chord[1]
            guess = self.make_guess_move()
            if guess[0]:
                return 'guess', guess[1]
        else:
            guess = self.make_guess_move()
            if guess[0]:
                return 'guess', guess[1]
            chord = self.make_chord_move()
            if chord[0]:
                return 'chord', chord[1]
        for key in animals:
            if comb(self.height * self.width, self.infos[key]['count'] - self.infos[key]['guess']) < 100000:
                self.solver.add_clauses(self.create_rule_animal_remaining(key, self.infos[key]['count'] - self.infos[key]['guess']))
            guess = self.make_guess_move()
            if guess[0]:
                return 'guess', guess[1]
        self.refresh_guess = True
        discover = self.make_discover_move()
        if discover[0]:
            return 'discover', discover[1]
        random = self.make_random_move()
        if random[0]:
            return 'discover', random[1]