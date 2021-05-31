from typing import List

def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)

def at_least_one(vars: List[int]) -> List[int]:
    return vars[:]

def main():
    print('Hello World')

if __name__ == "__main__":
    main()