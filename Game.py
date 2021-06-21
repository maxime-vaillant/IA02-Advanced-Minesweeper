import itertools
import subprocess
from sys import platform
from typing import List, Tuple, Dict

# F: Free, T: Tiger, S: Shark, C: Crocodile
values_list = ["F", "T", "S", "C"]
values_dict = {
    "F": 1,
    "T": 2,
    "S": 3,
    "C": 4,
}
length = len(values_dict)


class Game:
    """
    This class represents a game board
    """

    def __init__(self, height: int, width: int, tiger_count: int, shark_count: int, crocodile_count: int,
                 land_count: int, sea_count: int, filename: str = "default.cnf"):
        """
        Default constructor
        :param filename: name of the cnf file
        """
        self.width = width
        self.height = height
        self.file = filename
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
        self.clauses = []
        self.guest_moves = []
        self.response = []
        self.refresh_guess = True
        self.cmd = None
        if platform == 'darwin':
            self.cmd = "./gophersat/gophersat-1.1.6-MacOS"
        elif platform == 'win32':
            self.cmd = "./gophersat/gophersat-1.1.6-Windows"
        elif platform == 'linux':
            self.cmd = "./gophersat/gophersat-1.1.6-Linux"

    def exec_gophersat(self, encoding: str = "utf8") -> Tuple[bool, List[int]]:
        """
        Execute the current clauses
        :param encoding: encoding type
        :return: model results
        """
        if self.cmd:
            result = subprocess.run(
                [self.cmd, self.file], capture_output=True, check=True, encoding=encoding
            )
            string = str(result.stdout)
            lines = string.splitlines()

            if lines[1] != "s SATISFIABLE":
                return False, []

            model = lines[2][2:].split(" ")

            return True, [int(x) for x in model]
        else:
            print("Votre système d'exploitation n'est pas compatible")
            return False, []

    def write_dimacs_file(self, dimacs: str):
        """
        Write into the cnf file the new clauses
        :param dimacs: new clauses
        """
        with open(self.file, "w", newline="") as cnf:
            cnf.write(dimacs)

    @staticmethod
    def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int) -> str:
        """
        Change clauses to their dimacs value
        :param clauses: List of clauses
        :param nb_vars: number vars in the dimacs
        :return: dimacs value
        """
        end = "0\n"
        space = " "
        dimacs = "p cnf " + str(nb_vars) + space + str(len(clauses)) + "\n"
        for clause in clauses:
            for atom in clause:
                dimacs += str(atom) + space
            dimacs += end
        return dimacs

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

    def remove_useless_clauses(self):
        for i in range(self.height):
            for j in range(self.width):
                new_clauses = []
                if self.board[i][j]['type'] != '?':
                    new_clauses.append(self.cell_to_variable(i, j, self.board[i][j]['type']))
                    for key in values_dict:
                        if key != self.board[i][j]['type']:
                            new_clauses.append(-self.cell_to_variable(i, j, key))
                    for new in new_clauses:
                        for clause in self.clauses:
                            if new in clause:
                                self.clauses.remove(clause)
                        self.clauses.append([new])

    def filter_chord(self, item) -> bool:
        i, j = item
        cell = self.board[i][j]
        if cell['prox_count'] and sum(cell['prox_count']) == sum(cell['known_count'].values()) - cell['known_count']['F'] and sum(cell['known_count'].values()) != len(cell['near_cells']):
            return True
        return False

    def make_guess_move(self) -> Tuple[bool, Tuple]:
        if len(self.guest_moves) > 0:
            return True, self.guest_moves.pop(0)
        if self.refresh_guess:
            self.refresh_guess = False
            if self.height * self.width > 1000:
                self.remove_useless_clauses()
            # Find a model
            self.write_dimacs_file(self.clauses_to_dimacs(self.clauses, self.height * self.width * length))
            self.response = self.exec_gophersat()
            if self.response[0]:
                for var in self.response[1]:
                    if var > 0:
                        cell = self.variable_to_cell(var)
                        if cell[2] != 'F' and self.board[cell[0]][cell[1]]['type'] == '?':
                            # Try to deduct with UNSAT
                            self.write_dimacs_file(
                                self.clauses_to_dimacs(self.clauses + [[-var]], self.height * self.width * length))
                            deduction = self.exec_gophersat()
                            if not deduction[0]:
                                self.guest_moves.append(cell)
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
        if self.response[0]:
            for var in self.response[1]:
                if var > 0:
                    cell = self.variable_to_cell(var)
                    if cell[2] == 'F' and self.board[cell[0]][cell[1]]['type'] == '?':
                        # Try to deduct with UNSAT
                        self.write_dimacs_file(
                            self.clauses_to_dimacs(self.clauses + [[-var]], self.height * self.width * length))
                        deduction = self.exec_gophersat()
                        if not deduction[0]:
                            return True, cell
        return False, ()

    def make_random_move(self) -> Tuple[bool, Tuple]:
        sea_probability = (0 if self.infos["S"]["count"] == self.infos["S"]["guess"] else 1) if self.infos["sea"]["count"] == self.infos["sea"]["found"] else (self.infos["S"]["count"] - self.infos["S"]["guess"]) / (self.infos["sea"]["count"] - self.infos["sea"]["found"])
        land_probability = (0 if self.infos["T"]["count"] == self.infos["T"]["guess"] else 1) if self.infos["land"]["count"] == self.infos["land"]["found"] else (self.infos["T"]["count"] - self.infos["T"]["guess"]) / (self.infos["land"]["count"] - self.infos["land"]["found"])
        case_to_land = "sea" if sea_probability < land_probability else "land"
        random_move = []
        unsafe_move = []
        # TODO: Improve this part
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j]['type'] == '?':
                    if self.board[i][j]['field'] == case_to_land:
                        self.refresh_guess = True
                        return True, (i, j)
                    elif self.board[i][j]['field'] == '?':
                        random_move.append((i, j))
                    else:
                        unsafe_move.append((i, j))
        if len(random_move) > 0:
            self.refresh_guess = True
            return True, random_move[0]
        elif len(unsafe_move) > 0:
            self.refresh_guess = True
            return True, unsafe_move[0]
        return False, ()

    def add_information_constraints(self, data: Dict):
        i, j = data['pos']
        field = data['field']
        proximity_count = data.get('prox_count', None)
        guess_animal = data.get('animal', None)
        if guess_animal:
            # Increment guess count
            self.infos[guess_animal]['guess'] += 1
            # Add the guess on the board
            self.board[i][j]['type'] = guess_animal
            for cell in self.board[i][j]['near_cells']:
                self.board[cell[0]][cell[1]]['known_count'][guess_animal] += 1
            if self.infos[guess_animal]['count'] - self.infos[guess_animal]['guess'] == 1:
                self.clauses += self.create_rule_animal_remaining(guess_animal, 1)
                self.refresh_guess = True
        elif proximity_count:
            if [i, j] not in self.visitedCells:
                self.board[i][j]['field'] = field
                self.clauses.append([-self.cell_to_variable(i, j, "T") if field == "sea" else -self.cell_to_variable(i, j, "S")])
            # Increment field count
            self.infos[field]['found'] += 1
            self.board[i][j]['type'] = 'F'
            self.board[i][j]['prox_count'] = proximity_count
            self.clauses.append([self.cell_to_variable(i, j, 'F')])
            near_cells = self.board[i][j]['near_cells']
            for cell in near_cells:
                self.board[cell[0]][cell[1]]['known_count']['F'] += 1
                if cell not in self.visitedCells:
                    self.visitedCells.insert(0, cell)
                    self.clauses += self.create_rule_on_cell(cell[0], cell[1])
            animals = ("T", "S", "C")
            total_count = 0
            for index, count in enumerate(proximity_count):
                total_count += count
                cells = []
                animal = animals[index]
                for cell in near_cells:
                    cells.append(self.cell_to_variable(cell[0], cell[1], animal))
                self.clauses += self.exact(cells, count)
            cells = []
            for cell in near_cells:
                cells.append(self.cell_to_variable(cell[0], cell[1], "F"))
            self.clauses += self.exact(cells, len(near_cells) - total_count)
        else:
            self.board[i][j]['field'] = field
            self.clauses.append([-self.cell_to_variable(i, j, "T") if field == "sea" else -self.cell_to_variable(i, j, "S")])

    def make_decision(self) -> Tuple[str, Tuple]:
        if self.height * self.width > 2000:
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
        discover = self.make_discover_move()
        if discover[0]:
            return 'discover', discover[1]
        random = self.make_random_move()
        if random[0]:
            return 'discover', random[1]