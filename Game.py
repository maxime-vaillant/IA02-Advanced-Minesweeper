import itertools
import subprocess
from sys import platform
from typing import List, Tuple, Dict

# F: Free, T: Tiger, C: Crocodile, S: Shark
values_list = ["F", "T", "C", "S"]
values_dict = {
    "F": 1,
    "T": 2,
    "C": 3,
    "S": 4,
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
        # A cell is represented by a list ['?', []], the '?' represent the type of the cell ('F', 'T', 'S', 'C', 'F') and the [] is the proximity count.
        self.board = [[['?', []] for _ in range(width)] for _ in range(height)]
        self.file = filename
        self.cmd = None
        self.width = width
        self.height = height
        self.sea_count = sea_count
        self.land_count = land_count
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
            }
        }
        self.visitedCells = []
        self.clauses = []
        self.cells_infos = {}
        if platform == 'darwin':
            self.cmd = "./gophersat-1.1.6-MacOS"
        elif platform == 'win32':
            self.cmd = "./gophersat-1.1.6-Windows"
        elif platform == 'linux':
            self.cmd = "./gophersat-1.1.6-Linux"

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
        for c in self.visitedCells:
            # If cell can possibly handle a cord
            i = c[0]
            j = c[1]
            if self.board[i][j][1]:
                near_cells = self.get_near_cells(i, j)
                tiger_found = 0
                shark_found = 0
                crocodile_found = 0
                known = 0
                for cell in near_cells:
                    if self.board[cell[0]][cell[1]][0] == 'F':
                        known += 1
                    elif self.board[cell[0]][cell[1]][0] == 'T':
                        tiger_found += 1
                    elif self.board[cell[0]][cell[1]][0] == 'S':
                        shark_found += 1
                    elif self.board[cell[0]][cell[1]][0] == 'C':
                        crocodile_found += 1
                if tiger_found == self.board[i][j][1][0] and shark_found == self.board[i][j][1][1] and crocodile_found == self.board[i][j][1][2] and known + tiger_found + shark_found + crocodile_found != len(near_cells):
                    return 'chord', (i, j)
        self.write_dimacs_file(self.clauses_to_dimacs(self.clauses, self.height * self.width * length))
        response = self.exec_gophersat()
        best_move = ('none', ())
        best_score = 0
        vars = []
        if response[0]:
            for var in response[1]:
                if var > 0:
                    cell = self.variable_to_cell(var)
                    if self.board[cell[0]][cell[1]][0] == '?':
                        cell_infos = self.cells_infos.get(str([cell[0], cell[1]]), [0, 1])
                        score_cell = cell_infos[0] / 8
                        vars.append([var, cell, score_cell])
        vars.sort(key=lambda x: x[2], reverse=True)
        for v in vars:
            var = v[0]
            cell = v[1]
            score_cell = v[2]
            self.write_dimacs_file(self.clauses_to_dimacs(self.clauses+[[-var]], self.height * self.width * length))
            deduction = self.exec_gophersat()
            if not deduction[0]:
                if cell[2] == 'F':
                    return 'discover', cell
                else:
                    return 'guess', cell
            else:
                if score_cell >= best_score:
                    best_score = score_cell
                    if cell[2] == 'F':
                        best_move = ('discover', cell)
                    else:
                        best_move = ('guess', cell)
        # If in this case there is no response (fix of none error)
        if len(vars) == 0:
            for i in range(self.height):
                for j in range(self.width):
                    if self.board[i][j][0] == '?':
                        return 'discover', (i, j, 'F')
        return best_move

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
        cells = []
        for a in range(i - 1, i + 2):
            for b in range(j - 1, j + 2):
                if 0 <= a < self.height and 0 <= b < self.width and (a != i or b != j):
                    cells.append([a, b])
        return cells

    def get_adjacent_cells(self, i: int, j: int) -> List[List[int]]:
        cells = []
        for a in range(i - 1, i + 2):
            for b in range(j - 1, j + 2):
                if 0 <= a < self.height and 0 <= b < self.width and ((a != i and b == j) or (a == i and b != j)):
                    cells.append([a, b])
        return cells

    def create_rule_on_cell(self, i: int, j: int) -> List[List[int]]:
        cells = []
        for key in values_dict:
            cells.append(self.cell_to_variable(i, j, key))
        return self.exact(cells, 1)

    def create_rule_last_animal(self, animal: str, param: int) -> List[List[int]]:
        cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j][0] == '?':
                    cells.append(self.cell_to_variable(i, j, animal))
        return self.exact(cells, param)

    def add_information_constraints(self, data: Dict):
        pos = data["pos"]
        field = data["field"]
        clauses = [[-self.cell_to_variable(pos[0], pos[1], "T") if field == "sea" else -self.cell_to_variable(pos[0], pos[1], "S")]]
        proximity_count = data.get("prox_count", None)
        guess_animal = data.get("animal", None)
        if guess_animal:
            # Increment guess count
            self.infos[guess_animal]["guess"] += 1
            self.board[pos[0]][pos[1]][0] = guess_animal
            clauses.append([self.cell_to_variable(pos[0], pos[1], guess_animal)])
            if self.infos[guess_animal]["count"] - self.infos[guess_animal]["guess"] == 1:
                clauses += self.create_rule_last_animal(guess_animal, 1)
        if proximity_count:
            self.board[pos[0]][pos[1]] = ['F', proximity_count]
            clauses.append([self.cell_to_variable(pos[0], pos[1], 'F')])
            near_cells = self.get_near_cells(pos[0], pos[1])
            for cell in near_cells:
                if cell not in self.visitedCells:
                    self.visitedCells.append(cell)
                    clauses += self.create_rule_on_cell(cell[0], cell[1])
                cell_infos = self.cells_infos.get(str([cell[0], cell[1]]), None)
                if cell_infos:
                    self.cells_infos[str([cell[0], cell[1]])][0] += 1
                else:
                    self.cells_infos[str([cell[0], cell[1]])] = [1, len(self.get_near_cells(cell[0], cell[1]))]
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
        self.clauses += clauses
