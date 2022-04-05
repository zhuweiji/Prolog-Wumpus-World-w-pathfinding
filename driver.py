from pyswip import Prolog
from helpers import helper
from helpers import config

# creates walls.pl with wall information
helper.create_walls()

prolog = Prolog()
prolog.consult("driver.pl")


def generate_stench_rules(wumpus_coords):    
    max_x, max_y = config.MAP_SIZE
    stench_coords = []

    # Create stench rules
    for coordinates in wumpus_coords:
        X_Coord = coordinates[0]
        Y_Coord = coordinates[1]

        # Case 1 : wumpus @ corners
        if ((X_Coord == max_x or X_Coord == 1) and (Y_Coord == max_y or Y_Coord == 1)):
            if (X_Coord == max_x and Y_Coord == max_y):
                stench_coords.append([X_Coord, max_y-1])
                stench_coords.append([X_Coord-1, max_y])

            elif (X_Coord == 1 and Y_Coord == 1):
                stench_coords.append([1, 2])
                stench_coords.append([2, 1])
            
            elif (X_Coord == max_x and Y_Coord == 1):
                stench_coords.append([max_x-1, 1])
                stench_coords.append([max_x, 2])
            
            elif (X_Coord == 1 and Y_Coord == max_y):
                stench_coords.append([1, max_y-1])
                stench_coords.append([2, max_y])

        # Case 2 : wumpus @ wall but not corner
        elif (X_Coord == max_x or X_Coord == 1 or Y_Coord == max_y or Y_Coord == 1):
            if (X_Coord == 1):
                stench_coords.append([X_Coord,Y_Coord-1])
                stench_coords.append([X_Coord,Y_Coord+1])
                stench_coords.append([X_Coord+1,Y_Coord])
            
            elif (X_Coord == max_x):
                stench_coords.append([X_Coord,Y_Coord-1])
                stench_coords.append([X_Coord,Y_Coord+1])
                stench_coords.append([X_Coord-1,Y_Coord])

            elif (Y_Coord == 1):
                stench_coords.append([X_Coord-1, Y_Coord])
                stench_coords.append([X_Coord+1, Y_Coord])
                stench_coords.append([X_Coord, Y_Coord+1])
            
            elif (Y_Coord == max_y):
                stench_coords.append([X_Coord-1, Y_Coord])
                stench_coords.append([X_Coord+1, Y_Coord])
                stench_coords.append([X_Coord, Y_Coord-1])

        # Case 3 : wumpus not @ any wall
        else:
            stench_coords.append([X_Coord, Y_Coord-1])
            stench_coords.append([X_Coord, Y_Coord+1])
            stench_coords.append([X_Coord-1, Y_Coord])
            stench_coords.append([X_Coord+1, Y_Coord])
        
    return stench_coords


def map_generator():

    x,y = config.MAP_SIZE

    wumpus_coords = []
    gold_coords = []
    portal_coords = []

    for soln in prolog.query("wumpus_coords(X,Y)"):
        wumpus_coords.append([int(soln["X"]), int(soln["Y"])])
    
    for soln in prolog.query("gold_coords(X,Y)"):
        gold_coords.append([int(soln["X"]), int(soln["Y"])])

    for soln in prolog.query("portal_coords(X,Y)"):
        portal_coords.append([int(soln["X"]), int(soln["Y"])])

    stench_coords = generate_stench_rules(wumpus_coords)

    world_map = [['.','.','.','.','.','.','.'],
                ['.','.','.','.','.','.','.'],
                ['.','.','.','.','.','.','.'],
                ['.','.','.','.','.','.','.'],
                ['.','.','.','.','.','.','.'],
                ['.','.','.','.','.','.','.']]

    for i in range (0, x):
        for j in range(0, y):
            coords = [i,j]
            if coords in wumpus_coords:
                world_map[i][j] = 'W'
            elif coords in gold_coords:
                world_map[i][j] = 'G'
            elif coords in portal_coords:
                world_map[i][j] = 'P'
            elif coords in stench_coords:
                world_map[i][j] = 'S'


    for i in range (0, len(world_map)):
        for j in range(0, len(world_map[i])):
            print(world_map[i][j], end="\t")
        print()

    return world_map

if (__name__ == "__main__"):
    world_map = map_generator()
    