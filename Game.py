import subprocess
from sys import platform
from typing import List, Tuple
import itertools

values = ["Tiger", "Crocodile", "Shark", "Water", "Free", "Unknown"]
values_variables = {
    "Unknown": 1,
    "Free": 2,
    "Tiger":3,
    "Crocodile": 4,
    "Shark": 5,
    "Free": 6
}


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

    def write_dimacs_file(self, dimacs:str):
        """
        Write into the cnf file the new clauses
        :param dimacs: new clauses
        """
        with open(self.file, "w", newline="") as cnf:
            cnf.write(dimacs)

    def cell_to_variable(self, cell: Tuple[int, int, str]):
        """
        Transform a cell representation to a variable
        :param cell:
        :return:
        """
        return cell[0] + cell[1]*self.width + values_variables(cell[2])

    def variable_to_cell(self, var: int) -> Tuple[int, int, str]:
        """
        Change a variable to his cell value
        :param var: variable
        :return: cell
        """
        case = var // len(values)
        return [case % self.width, case//self.width, var%len(values)]

    def at_least_one(self, vars: List[int]) -> List[int]:
        return vars[:]

    def unique(self, vars: List[List[int]]) -> List[List[int]]:
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

    def create_game_constraints(self):
        """
        Init the clauses
        :param w: width of the board
        :param h: height of the board
        """
        clauses = []
        var = []

        # TODO create clauses

        for x in range(self.width):
            for y in range (self.height):
                for value in values:
                    var.append([x, y, value])

        for tempVar in var:
            clauses += tempVar[0]+tempVar[1]+values_variables(tempVar[2])

        clauses = self.unique(clauses)

        self.write_dimacs_file(self.clauses_to_dimacs(clauses, 6*self.width*self.height))

    def clauses_to_dimacs(self, clauses: List[List[int]], nb_vars: int) -> str:
        """
        Change clauses to their dimacs value
        :param clauses: List of clauses
        :param nb_vars: number vars in the dimacs
        :return: dimacs value
        """
        return ''
