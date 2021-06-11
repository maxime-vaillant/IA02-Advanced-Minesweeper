import subprocess
from sys import platform
from typing import List, Tuple, Dict
import itertools

# U: Unknown, F: Free, T: Tiger, C: Crocodile, S: Shark, W: Water
values_list = ["L", "W", "F", "T", "C", "S"]
values_dict = {
    "L": 1,
    "W": 2,
    "F": 3,
    "T": 4,
    "C": 5,
    "S": 6,
}
length = len(values_dict)


class Game:
    """
    This class represents a game board
    """

    def __init__(self, height: int, width: int, tiger_count: int, crocodile_count: int, shark_count: int,
                 land_count: int, sea_count: int, filename: str = "default.cnf"):
        """
        Default constructor
        :param filename: name of the cnf file
        """
        self.board = [[['?', '?', []] for j in range(width)] for i in range(height)]
        self.file = filename
        self.cmd = None
        self.width = width
        self.height = height
        self.sea_count = sea_count
        self.land_count = land_count
        self.crocodile_count = crocodile_count
        self.tiger_count = tiger_count
        self.shark_count = shark_count
        self.visitedCells = []
        self.clauses = []
        if platform == 'darwin':
            self.cmd = "./gophersat-1.1.6-MacOS"
        elif platform == 'win32':
            self.cmd = "./gophersat-1.1.6-Windows"
        elif platform == 'linux':
            self.cmd = "./gophersat-1.1.6-Linux"

    def make_decision(self) -> Tuple[str, Tuple]:
        self.write_dimacs_file(self.clauses_to_dimacs(self.clauses, self.height * self.width * length))
        response = self.exec_gophersat()
        free = []
        guess = []
        if response[0]:
            for var in response[1]:
                if var > 0:
                    cell = self.variable_to_cell(var)
                    if self.board[cell[0]][cell[1]][1] == '?' and cell[2] != 'W' and cell[2] != 'L':
                        if cell[2] == 'F':
                            free.append(cell)
                        else:
                            guess.append(cell)
        if len(free) > 0:
            return 'discover', free[0]
        elif len(guess) > 0:
            return 'guess', guess[0]
        else:
            return 'none', ()

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
        :param i:
        :param j:
        :param val:
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
        Take a list of clauses and remove all duplicates ones
        :param param: number exact
        :param vars: in clauses list
        :return: list of unique clauses
        """
        clauses = [self.at_least_one(vars)] if param != 0 or param == len(vars) else []
        clauses += [[x] for x in vars] if param == len(vars) else []
        for combination in itertools.combinations([-x for x in vars[:]], param + 1):
            clause = []
            for i in range(param + 1):
                clause.append(combination[i])
            clauses.append(clause)
        return clauses

    def getNearCells(self, i: int, j: int) -> List[List[int]]:
        cells = []
        for a in range(i - 1, i + 2):
            for b in range(j - 1, j + 2):
                if 0 <= a < self.height and 0 <= b < self.width and (a != i or b != j):
                    cells.append([a, b])
        return cells

    def create_rule_on_cell(self, i: int, j: int) -> List[List[int]]:
        clauses = []
        cells = []
        for key in values_dict:
            if key != "W" and key != "L":
                cells.append(self.cell_to_variable(i, j, key))
            elif key == "T":
                clauses.append([-self.cell_to_variable(i, j, key), -self.cell_to_variable(i, j, "W")])
            elif key == "S":
                clauses.append([-self.cell_to_variable(i, j, key), -self.cell_to_variable(i, j, "L")])
        clauses += self.exact(cells, 1)
        clauses.append([self.cell_to_variable(i, j, "W"), self.cell_to_variable(i, j, "L")])
        clauses.append([-self.cell_to_variable(i, j, "W"), -self.cell_to_variable(i, j, "L")])
        return clauses

    def add_information_constraints(self, data: Dict):
        clauses = []
        pos = data["pos"]
        field = data["field"]
        f = self.cell_to_variable(pos[0], pos[1], "W") if field == "sea" else -self.cell_to_variable(pos[0], pos[1],
                                                                                                     "L")
        proximity_count = data.get("prox_count", None)
        guess_animal = data.get("animal", None)
        if guess_animal:
            self.board[pos[0]][pos[1]][1] = guess_animal
            clauses.append([self.cell_to_variable(pos[0], pos[1], guess_animal)])
        if proximity_count:
            self.board[pos[0]][pos[1]] = ["W" if field == "sea" else "L", 'F', proximity_count]
            clauses.append([self.cell_to_variable(pos[0], pos[1], 'F')])
            near_cells = self.getNearCells(pos[0], pos[1])
            for cell in near_cells:
                if cell not in self.visitedCells:
                    self.visitedCells.append(cell)
                    clauses += self.create_rule_on_cell(cell[0], cell[1])
            animals = ("T", "S", "C")
            total_count = 0
            for index, count in enumerate(proximity_count):
                total_count += count
                cells = []
                animal = animals[index]
                for cell in near_cells:
                    cells.append(self.cell_to_variable(cell[0], cell[1], animal))
                clauses += self.exact(cells, count)
            cells = []
            for cell in near_cells:
                cells.append(self.cell_to_variable(cell[0], cell[1], "F"))
            clauses += self.exact(cells, len(near_cells) - total_count)
        else:
            self.board[pos[0]][pos[1]][0] = "W" if field == "sea" else "L"
        clauses.append([f])
        self.clauses += clauses
