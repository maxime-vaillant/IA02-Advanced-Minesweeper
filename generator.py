import os
import glob
from random import randrange, random

WIDTH_MAP = 10
HEIGHT_MAP = 10
CHANCE_ANIMAL = 0.1
ANIMALS = ['S', 'W', 'C', 'T']
VOID = ['~', '-']

def randomTerrain(x, y, tab):
    try:
        tab[y][x] = (VOID[randrange(len(VOID))])
    except Exception:
        print('Start is on the edge of the board')

def main():
    # Get a list of all the file paths that ends with .txt from in specified directory
    fileList = glob.glob('./crocomine/grids/mapGenerated*.croco')
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

    # Generate each map
    nbMap = input("Enter number of map: ")
    for i in range(int(nbMap)):
        # Map information
        f = open("./crocomine/grids/mapGenerated" + str(i) + ".croco", "a")
        f.write("Map generated number " + str(i) + '\n')
        f.write(str(HEIGHT_MAP) + ' ' + str(WIDTH_MAP) + '\n')

        # Starting point
        start_x = randrange(WIDTH_MAP)
        start_y = randrange(HEIGHT_MAP)
        f.write(str(start_y) + ' ' + str(start_x))

        # Creation of a matrice that represents the map
        map = []
        for y in range(HEIGHT_MAP):
            line = []
            for x in range(WIDTH_MAP):
                if random() < CHANCE_ANIMAL:
                    line.append(ANIMALS[randrange(len(ANIMALS))])
                else:
                    line.append(VOID[randrange(len(VOID))])
            map.append(line)

        # Changing animals on starting point
        randomTerrain(start_x, start_y, map)
        randomTerrain(start_x+1, start_y, map)
        randomTerrain(start_x+1, start_y+1, map)
        randomTerrain(start_x+1, start_y-1, map)
        randomTerrain(start_x, start_y+1, map)
        randomTerrain(start_x-1, start_y+1, map)
        randomTerrain(start_x-1, start_y-1, map)
        randomTerrain(start_x-1, start_y, map)
        randomTerrain(start_x, start_y-1, map)

        for line in map:
            f.write("\n")
            for value in range(len(line)):
                (value < len(line) - 1) if (f.write(line[value] + ' ')) else (f.write(line[value]))
        f.write('\n')
        f.close()
    print("Generation Fini!")


if __name__ == "__main__":
    main()
