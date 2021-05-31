import itertools
import subprocess
from typing import List, Tuple
from sys import platform

variables = ["Tiger", "Crocodile", "Shark", "Water", "Free", "Unknown"]

def exec_gophersat(filename: str, encoding: str = "utf8") -> Tuple[bool, List[int]]:
    cmd = None

    if platform == 'darwin':
        cmd = "./gophersat-1.1.6-MacOS"
    elif platform == 'win32':
        cmd = "./gophersat-1.1.6-Windows"
    elif platform == 'linux':
        cmd = "./gophersat-1.1.6-Linux"

    if cmd:
        result = subprocess.run(
            [cmd, filename], capture_output=True, check=True, encoding=encoding
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

def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)

def cell_to_variable(i: int, j: int, val: str) -> int:
    return

def variable_to_cell(var: int) -> Tuple[int, int, str]:
    return

def at_least_one(vars: List[int]) -> List[int]:
    return vars[:]

def unique(vars: List[int]) -> List[List[int]]:
    clauses = [at_least_one(vars)]
    for clause in itertools.combinations([-x for x in vars[:]], 2):
        i, j = clause
        clauses.append([i, j])
    return clauses

def create_animal_constraints(m: int, n: int) -> List[List[int]]:
    clauses = []

    return clauses

def main():
    print(platform)

if __name__ == "__main__":
    main()