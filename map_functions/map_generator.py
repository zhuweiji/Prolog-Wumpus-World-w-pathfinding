from helpers import config
from pyswip import Prolog

prolog = Prolog()
prolog.consult("../map.pl")

def generate_surrounding_indicators(item_coords):    
    max_x, max_y = config.MAP_SIZE
    item_indicator_coords = []

    # Create item_indicator rules
    for coordinates in item_coords:
        X_Coord = coordinates[0]
        Y_Coord = coordinates[1]

        # Case 1 : item @ corners
        if ((X_Coord == max_x or X_Coord == 1) and (Y_Coord == max_y or Y_Coord == 1)):
            if (X_Coord == max_x and Y_Coord == max_y):
                item_indicator_coords.append([X_Coord, max_y-1])
                item_indicator_coords.append([X_Coord-1, max_y])

            elif (X_Coord == 1 and Y_Coord == 1):
                item_indicator_coords.append([1, 2])
                item_indicator_coords.append([2, 1])
            
            elif (X_Coord == max_x and Y_Coord == 1):
                item_indicator_coords.append([max_x-1, 1])
                item_indicator_coords.append([max_x, 2])
            
            elif (X_Coord == 1 and Y_Coord == max_y):
                item_indicator_coords.append([1, max_y-1])
                item_indicator_coords.append([2, max_y])

        # Case 2 : item @ wall but not corner
        elif (X_Coord == max_x or X_Coord == 1 or Y_Coord == max_y or Y_Coord == 1):
            if (X_Coord == 1):
                item_indicator_coords.append([X_Coord,Y_Coord-1])
                item_indicator_coords.append([X_Coord,Y_Coord+1])
                item_indicator_coords.append([X_Coord+1,Y_Coord])
            
            elif (X_Coord == max_x):
                item_indicator_coords.append([X_Coord,Y_Coord-1])
                item_indicator_coords.append([X_Coord,Y_Coord+1])
                item_indicator_coords.append([X_Coord-1,Y_Coord])

            elif (Y_Coord == 1):
                item_indicator_coords.append([X_Coord-1, Y_Coord])
                item_indicator_coords.append([X_Coord+1, Y_Coord])
                item_indicator_coords.append([X_Coord, Y_Coord+1])
            
            elif (Y_Coord == max_y):
                item_indicator_coords.append([X_Coord-1, Y_Coord])
                item_indicator_coords.append([X_Coord+1, Y_Coord])
                item_indicator_coords.append([X_Coord, Y_Coord-1])

        # Case 3 : item not @ any wall
        else:
            item_indicator_coords.append([X_Coord, Y_Coord-1])
            item_indicator_coords.append([X_Coord, Y_Coord+1])
            item_indicator_coords.append([X_Coord-1, Y_Coord])
            item_indicator_coords.append([X_Coord+1, Y_Coord])
        
    return item_indicator_coords

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

    stench_coords = generate_surrounding_indicators(wumpus_coords)
    tingle_coords = generate_surrounding_indicators(portal_coords)

    world_map = [['','','','','','',''],
                ['','','','','','',''],
                ['','','','','','',''],
                ['','','','','','',''],
                ['','','','','','',''],
                ['','','','','','','']]

    for i in range (0, y):
        for j in range(0, x):
            coords = [j+1,i+1]
            if coords in wumpus_coords:
                world_map[i][j] += 'W'
            if coords in gold_coords:
                world_map[i][j] += '*'
            if coords in portal_coords:
                world_map[i][j] += 'O'
            if coords in stench_coords:
                world_map[i][j] += '='
            if coords in tingle_coords:
                world_map[i][j] += 'T'
            if (world_map[i][j] == ''):
                world_map[i][j] = '.'

    # for i in range (0, len(world_map)):
    #     for j in range(0, len(world_map[i])):
    #         print(world_map[i][j], end="\t")
    #     print()

    return world_map

