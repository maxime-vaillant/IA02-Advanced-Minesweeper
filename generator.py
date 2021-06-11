import os
import glob
from random import randrange, random


def main():
    WIDTH_MAP = 10
    HEIGHT_MAP = 10
    CHANCE_ANIMAL = 0.1
    ANIMALS = ['S', 'W', 'T', 'C']
    VOID = ['-', '~']
    # Get a list of all the file paths that ends with .txt from in specified directory
    fileList = glob.glob('./crocomine/grids/mapGenerated*.croco')
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

    # generate maps
    nbMap = input("Enter number of map: ")
    for i in range(int(nbMap)):
        # Map information
        f = open("./crocomine/grids/mapGenerated"+str(i)+".croco", "a")
        f.write("Map generated number " + str(i)+'\n')
        f.write(str(HEIGHT_MAP) + ' ' + str(WIDTH_MAP)+'\n')

        # Starting point
        startX = randrange(WIDTH_MAP)
        startY = randrange(HEIGHT_MAP)
        f.write(str(startX) + ' ' + str(startY))
        map = [[]] 

        for y in range(HEIGHT_MAP):
            f.write("\n")
            for x in range(WIDTH_MAP):
                if random() < CHANCE_ANIMAL:
                    f.write(ANIMALS[randrange(3)])
                else:
                    f.write(VOID[randrange(2)])
                if x < WIDTH_MAP-1:
                    f.write(' ')

        # delete terrain on start
        if

        f.close()
    print("Generation Fini!")



if __name__ == "__main__":
    main()