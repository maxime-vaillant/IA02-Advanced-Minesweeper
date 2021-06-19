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
        # A cell is represented by a list ['?', [], '?'], the first '?' represent the type of the cell ('F', 'T', 'S', 'C'), the [] is the proximity count and the last '?' the field.
        self.board = [[['?', [], '?'] for _ in range(width)] for _ in range(height)]
        self.file = filename
        self.width = width
        self.height = height
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
        self.cells_infos = {}
        self.guest_moves = []
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
                if self.board[i][j][0] == '?':
                    cells.append(self.cell_to_variable(i, j, animal))
        return self.exact(cells, param)

    def remove_useless_clauses(self):
        for i in range(self.height):
            for j in range(self.width):
                new_clauses = []
                if self.board[i][j][0] != '?':
                    new_clauses.append(self.cell_to_variable(i, j, self.board[i][j][0]))
                    for key in values_dict:
                        if key != self.board[i][j][0]:
                            new_clauses.append(-self.cell_to_variable(i, j, key))
                    for new in new_clauses:
                        for clause in self.clauses:
                            if new in clause:
                                self.clauses.remove(clause)
                        self.clauses.append([new])

    def add_information_constraints(self, data: Dict):
        pos = data["pos"]
        field = data["field"]
        proximity_count = data.get("prox_count", None)
        guess_animal = data.get("animal", None)
        if guess_animal:
            # Increment guess count
            self.infos[guess_animal]["guess"] += 1
            # Add the guess on the board
            self.board[pos[0]][pos[1]][0] = guess_animal
            # The following line seems to be useless
            # clauses.append([self.cell_to_variable(pos[0], pos[1], guess_animal)])
            if self.infos[guess_animal]["count"] - self.infos[guess_animal]["guess"] == 1:
                self.clauses += self.create_rule_animal_remaining(guess_animal, 1)
        elif proximity_count:
            if [pos[0], pos[1]] not in self.visitedCells:
                self.board[pos[0]][pos[1]][2] = field
                self.clauses.append([-self.cell_to_variable(pos[0], pos[1], "T") if field == "sea" else -self.cell_to_variable(pos[0], pos[1], "S")])
            # Increment field count
            self.infos[field]["found"] += 1
            self.board[pos[0]][pos[1]] = ['F', proximity_count]
            self.clauses.append([self.cell_to_variable(pos[0], pos[1], 'F')])
            near_cells = self.get_near_cells(pos[0], pos[1])
            for cell in near_cells:
                if cell not in self.visitedCells:
                    self.visitedCells.insert(0, cell)
                    self.clauses += self.create_rule_on_cell(cell[0], cell[1])
                cell_infos = self.cells_infos.get(str([cell[0], cell[1]]), None)
                if cell_infos:
                    self.cells_infos[str([cell[0], cell[1]])] += 1
                else:
                    self.cells_infos[str([cell[0], cell[1]])] = 1
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
            self.board[pos[0]][pos[1]][2] = field
            self.clauses.append([-self.cell_to_variable(pos[0], pos[1], "T") if field == "sea" else -self.cell_to_variable(pos[0], pos[1], "S")])

    def make_decision(self) -> Tuple[str, Tuple]:
        """ Debug
        for clause in self.clauses:
            for c in clause:
                if c > 0:
                    print(self.variable_to_cell(c), end='')
                else:
                    print(" -", self.variable_to_cell(-c), end='')
            print()
        """
        # Cord search
        for v in self.visitedCells:
            i = v[0]
            j = v[1]
            board_cell = self.board[i][j][1]
            if board_cell:
                near_cells = self.get_near_cells(i, j)
                found_count = {
                    'F': 0,
                    'T': 0,
                    'S': 0,
                    'C': 0,
                }
                for cell in near_cells:
                    if self.board[cell[0]][cell[1]][0] != '?':
                        found_count[self.board[cell[0]][cell[1]][0]] += 1
                # If cell can possibly handle a cord
                if found_count['T'] == board_cell[0] and found_count['S'] == board_cell[1] and found_count['C'] == board_cell[2] and sum(found_count.values()) != len(near_cells):
                    return 'chord', (i, j)
        # Guess all cells we know
        if len(self.guest_moves) > 0:
            return 'guess', self.guest_moves.pop(0)
        self.remove_useless_clauses()
        discover_moves = []
        # Find a model
        self.write_dimacs_file(self.clauses_to_dimacs(self.clauses, self.height * self.width * length))
        response = self.exec_gophersat()
        if response[0]:
            for var in response[1]:
                if var > 0:
                    cell = self.variable_to_cell(var)
                    if self.board[cell[0]][cell[1]][0] == '?':
                        # Try to deduct with UNSAT
                        self.write_dimacs_file(self.clauses_to_dimacs(self.clauses+[[-var]], self.height * self.width * length))
                        deduction = self.exec_gophersat()
                        if not deduction[0]:
                            if cell[2] == 'F':
                                discover_moves.append(cell)
                            else:
                                self.guest_moves.append(cell)
        if len(self.guest_moves) > 0:
            return 'guess', self.guest_moves.pop(0)
        elif len(discover_moves) > 0:
            return 'discover', discover_moves[0]
        # If in this case there is no response (fix of none error)
        else:
            sea_probability = (0 if self.infos["S"]["count"] == self.infos["S"]["guess"] else 1) if self.infos["sea"]["count"] == self.infos["sea"]["found"] else (self.infos["S"]["count"] - self.infos["S"]["guess"]) / (self.infos["sea"]["count"] - self.infos["sea"]["found"])
            land_probability = (0 if self.infos["T"]["count"] == self.infos["T"]["guess"] else 1) if self.infos["land"]["count"] == self.infos["land"]["found"] else (self.infos["T"]["count"] - self.infos["T"]["guess"]) / (self.infos["land"]["count"] - self.infos["land"]["found"])
            case_to_land = "sea" if sea_probability < land_probability else "land"
            random_move = []
            unsafe_move = []
            # TODO: Improve this part
            for i in range(self.height):
                for j in range(self.width):
                    if self.board[i][j][0] == '?':
                        if self.board[i][j][2] == case_to_land:
                            return 'discover', (i, j, 'F')
                        elif self.board[i][j][2] == '?':
                            random_move.append((i, j))
                        else:
                            unsafe_move.append((i, j))
            if len(random_move) > 0:
                return 'discover', random_move[0]
            elif len(unsafe_move) > 0:
                return 'discover', unsafe_move[0]
            else:
                return 'none', ()