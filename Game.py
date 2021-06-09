import subprocess
from sys import platform
from typing import List, Tuple
import itertools

# U: Unknown, F: Free, T: Tiger, C: Crocodile, S: Shark, W: Water
values_list = ["U", "F", "T", "C", "S", "W"]
values_dict = {
    "U": 1,
    "F": 2,
    "T": 3,
    "C": 4,
    "S": 5,
    "W": 6
}
length = len(values_dict)


class Game:
    """
    This class represents a game board
    """

    def __init__(self, width: int, height: int, filename: str = "default.cnf"):
        """
        Default constructor
        :param filename: name of the cnf file
        """
        self.board = []
        self.file = filename
        self.cmd = None
        self.width = width
        self.height = height
        if platform == 'darwin':
            self.cmd = "./gophersat-1.1.6-MacOS"
        elif platform == 'win32':
            self.cmd = "./gophersat-1.1.6-Windows"
        elif platform == 'linux':
            self.cmd = "./gophersat-1.1.6-Linux"
        self.create_game_constraints()

    def make_decision(self, data_received) -> Tuple[int, int, str]:
        """
        Call on each click, make a new decision and choose a position to do an action
        :param data_received: string received by the api
        :return: tuple representing the client action : position click, action
        """

        solve = self.exec_gophersat()

        # TODO check if can stop

        # TODO update clauses

        return False

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
        i, rest = var // (self.width * length), var % (self.width * length)
        j, rest = rest // length, rest % length
        val = values_list[rest-1]
        return i, j, val

    def at_least_one(self, vars: List[int]) -> List[int]:
        return vars[:]

    def unique(self, vars: List[int]) -> List[List[int]]:
        """
        Take a list of clauses and remove all duplicates ones
        :param vars: in clauses list
        :return: list of unique clauses
        """
        clauses = [self.at_least_one(vars)]
        for clause in itertools.combinations([-x for x in vars[:]], 2):
            i, j = clause
            clauses.append([i, j])
        return clauses

    # Création des règles liées aux animaux
    # On applique les règles pour toutes les cases du démineur
    # unique: U v F v C v S v T
    # -T v -W
    # -S v W
    def create_animals_constraints(self) -> List[List[int]]:
        clauses = []
        for i in range(self.height):
            for j in range(self.width):
                cells = []
                for key in values_dict:
                    if key != "W":
                        cells.append(self.cell_to_variable(i, j, key))
                    if key == "U":
                        clauses.append([self.cell_to_variable(i, j, key)])
                    elif key == "T":
                        clauses.append([-self.cell_to_variable(i, j, key), -self.cell_to_variable(i, j, "W")])
                    elif key == "S":
                        clauses.append([-self.cell_to_variable(i, j, key), self.cell_to_variable(i, j, "W")])
                clauses += self.unique(cells)
        return clauses

    def create_game_constraints(self):
        """
        Init the clauses
        """
        clauses = []

        clauses += self.create_animals_constraints()

        # TODO create clauses

        self.write_dimacs_file(self.clauses_to_dimacs(clauses, length * self.width * self.height))

    def clauses_to_dimacs(self, clauses: List[List[int]], nb_vars: int) -> str:
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
