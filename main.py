import itertools
import subprocess
from typing import List, Tuple
from sys import platform

from Game import Game


def main():
    # TODO Get first values from the api

    game = Game(4, 4)

    print(game.exec_gophersat())

    end = False


if __name__ == "__main__":
    main()