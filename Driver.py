import enum
import traceback
from random import randint

from pyswip import Prolog
from prolog_agent import printer


# import constants.MapConsts as MapConsts
# from models.MapBuilder import MapBuilder

'''
List of constants regarding the map
'''
MAX_VALID_COL = 4
MIN_VALID_COL = 1
MAX_VALID_ROW = 5
MIN_VALID_ROW = 1

MAX_COL = 5
MAX_ROW = 6


class ArrowState(enum.Enum):
	UNUSED = 0
	MISSED = 1
	HIT = 2


class AgentState(enum.Enum):
	ALIVE = 0
	DEAD = 1
	ESCAPED = 2

class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, direction):
        return Coordinate(self.x + direction.getX(), self.y + direction.getY())

    def minus(self, c):
        return Coordinate(self.x - c.x, self.y - c.y)

    def __str__(self) -> str:
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y

    def __hash__(self) -> int:
        return (self.y * 45) + self.x  # Coordinates have unique x and y


class Direction(enum.Enum):
    North = 0, (0, 1)
    East = 1, (1, 0)
    South = 2, (0, -1)
    West = 3, (-1, 0)

    def __init__(self, ordinal, delta):
        super().__init__()
        self.ordinal = ordinal
        self.x = delta[0]
        self.y = delta[1]

    def right(self):
        all_values = [d.name for d in Direction]
        i = self.value[0] + 1 # ordinal
        if i == len(all_values):
            i = 0
        return Direction[str(all_values[i])]

    def left(self):
        all_values = [d.name for d in Direction]
        i = self.value[0] # ordinal
        if i == 0:
            i = len(all_values) - 1
        else:
            i = i-1
        return Direction[str(all_values[i])]

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def rand_direction():
        all_values = [d.name for d in Direction]
        i = randint(0, 3)
        return Direction[str(all_values[i])]

class Agent:
    def __init__(self, start, direction):
        self.location = start
        self.direction = direction
        self.agentState = AgentState.ALIVE
        self.arrowState = ArrowState.UNUSED
        # self.hasObtainedGold = False
        self.prolog = Prolog() # TODO remove this
        self.prevLocation = Coordinate(0,0)

    def setProlog(self, prolog) -> None:
        self.prolog = prolog

    def explore(self):
        queried_explore = list(self.prolog.query("explore(L).", maxresult=1))
        # print(queried_explore)
        moves_string_arr = []
        for e in queried_explore:
            for atom in (e['L']):
                moves_string_arr.append(str(atom))
        return moves_string_arr

    def rebornPrologAgent(self) -> bool:
        isGoodResetQuery = bool(list(self.prolog.query("reborn.")))
        walls_test = list(self.prolog.query("wall(X, Y).")) 
        wumpus_test = list(self.prolog.query("wumpus(X, Y).")) 
        confunduses_test = list(self.prolog.query("confundus(X, Y).")) 
        tingle_test = list(self.prolog.query("tingle(X, Y).")) 
        glitter_test = list(self.prolog.query("glitter(X, Y).")) 
        visited_test = list(self.prolog.query("visited(X, Y).")) 
        safe_test = list(self.prolog.query("safe(X, Y).")) 
        safe_test.pop()

        if not(isGoodResetQuery) or len(walls_test) != 0 or\
            len(wumpus_test) != 0 or len(confunduses_test) != 0 or\
            len(tingle_test) != 0 or len(glitter_test) != 0 or\
            len(safe_test) != 1:
            print(walls_test)
            print(wumpus_test)
            print(confunduses_test)
            print(tingle_test)
            print(glitter_test)
            print(safe_test)
            raise Exception("Prolog Agent Map was not reset properly")

    def getReasonedNpcOrSenseByName(self, npcName):
        queried = list(self.prolog.query(f"{npcName}(X, Y)."))
        npcs = set()
        for w in queried:
            _c = Coordinate(w['X'], w['Y'])
            npcs.add(_c)
        return npcs

    def executeMove(self, move, sensorIndicators):
        test = list(self.prolog.query(f"move({move}, {sensorIndicators})"))
        # print(test)


    def executeReposition(self, sensorIndicators):
        sensorIndicators[0] = "on"
        list(self.prolog.query(f"reposition({sensorIndicators})"))

    def resetAgent(self):
        self.location = Coordinate(0, 0)
        self.direction = Direction.North


    def getLocation(self) -> Coordinate:
        return self.location

    def setLocation(self, location) -> None:
        self.location = location

    def getDirection(self) -> Direction:
        return self.direction

    def setDirection(self, direction) -> None:
        self.direction = direction

    # def hasObtainedGold(self) -> bool:
    #     return self.hasObtainedGold

    # def setHasObtainedGold(self, hasObtainedGold) -> None:
    #     self.hasObtainedGold = hasObtainedGold

    def moveForward(self) -> None:
        self.prevLocation = self.location
        self.location = self.location.move(self.direction)
        return self.location

    def turnRight(self) -> None:
        self.direction = self.direction.right()
        return self.direction
    
    def turnLeft(self) -> None:
        self.direction = self.direction.left()
        return self.direction

    def setMissedWumpus(self) -> None:
        self.arrowState = ArrowState.MISSED

    def setKilledWumpus(self) -> None:
        self.arrowState = ArrowState.HIT

    def hasArrow(self) -> bool:
        return self.arrowState == ArrowState.UNUSED
    
    def haveKilledWumpus(self) -> bool:
        return self.arrowState == ArrowState.HIT


class MapBuilder:

    def __init__(self) -> None:
        self.wumpus = None
        self.golds = set()
        self.home = None
        self.agent = None
        self.confunduses = []
        self.walls = set()

    def buildMap(self):
        self.gen_wumpus_coords()
        self.gen_gold_coords()
        self.gen_confunduses_coords()
        self.gen_agent()
        self.gen_wall_coords()

    def gen_wumpus_coords(self):
        self.wumpus = self.randCoord()

    def gen_gold_coords(self):
        max_gold_count = randint(1, 3)
        is_valid = False

        while(is_valid != True):
            self.golds.clear()
            count = 0
            while(count != max_gold_count):
                self.golds.add(self.randCoord())
                count += 1
            is_valid = self.checkCoordIsInOtherNPCs()

    def gen_agent(self):
        is_valid = False
        while(is_valid != True):
            self.home = self.randCoord()
            is_valid = self.checkCoordIsInOtherNPCs() and self.checkAgentIsAdjacentToWumpusConfun()

        rand_dir = Direction.rand_direction()
        self.agent = Agent(self.home, rand_dir)

    def gen_confunduses_coords(self):
        is_valid = False
        confunduses_set = set()
        while(is_valid != True):
            confunduses_set.clear()
            while(len(confunduses_set) != 1):
                c = self.randCoord()
                confunduses_set.add(c)
            self.confunduses = list(confunduses_set)
            is_valid = self.checkCoordIsInOtherNPCs()


    def gen_wall_coords(self):
        walls = set()
        for i in range(7):
            walls.add(Coordinate(0, i))
            walls.add(Coordinate(5, i))

        for i in range(1, 5):
            walls.add(Coordinate(i, 0))
            walls.add(Coordinate(i, 6))

        self.walls = walls

    def checkCoordIsInOtherNPCs(self):
        test_set = set()
        count = 0
        if self.wumpus is not None:
            test_set.add(self.wumpus)
            count += 1
        # if self.golds is not None:
        #     test_set.add(self.golds)
        #     count += 1
        if self.home is not None:
            test_set.add(self.home)
            count += 1
        
        if len(self.golds) > 0:
            for g in self.golds:
                test_set.add(g)
                count += 1

        if len(self.confunduses) > 0:
            for c in self.confunduses:
                test_set.add(c)
                count += 1

        if len(test_set) != count:
            return False

        return True

    # TODO Assumption we made, may need to remove when testing against other drivers
    def checkAgentIsAdjacentToWumpusConfun(self):
        if self.wumpus is not None:
            if self.home in self.adjacentCoordinates(self.wumpus):
                return False
        
        if len(self.confunduses) > 0:
            for c in self.confunduses:
                if self.home in self.adjacentCoordinates(c):
                    return False
        return True

    def adjacentCoordinates(self, c):
        return [Coordinate(c.x-1, c.y), Coordinate(c.x+1, c.y), Coordinate(c.x, c.y+1), Coordinate(c.x, c.y-1)]

    def randCoord(self) -> Coordinate:
        return Coordinate(self.gen_valid_col_int(), self.gen_valid_row_int())

    def gen_valid_col_int(self) -> int:
        return randint(MIN_VALID_COL, MAX_VALID_COL)

    def gen_valid_row_int(self) -> int:
        return randint(MIN_VALID_ROW, MAX_VALID_ROW)


class AbsoluteMap:
    def __init__(self) -> None:
        self.mapBuilder = MapBuilder()
        self.mapBuilder.buildMap()
        self.home = self.mapBuilder.agent.getLocation() # where to return to
        self.golds = self.mapBuilder.golds
        self.wumpus = self.mapBuilder.wumpus
        self.confunduses = self.mapBuilder.confunduses
        self.agent = self.mapBuilder.agent
        self.walls = self.mapBuilder.walls
        # Test code
        # self.agent = Agent(Coordinate(2,1), Direction.North)
        # self.wumpus = Coordinate(2,2)
        # self.agent = Agent(Coordinate(2,1), Direction.North)
        # self.wumpus = Coordinate(2,3)
        # self.confunduses = [Coordinate(2,2)]


    def generateSensorIndicators(self, isShooting=False):
        sensorIndicators = ["off", "off", "off", "off", "off", "off"]

        # should always be run regardless of type of move
        if self.isWumpus(self.agent.getLocation()): # TODO can refactor to remove self.agent.getLocation()
            lol = ["stomped", "eaten", "squashed", "flatten", "castrated"]
            errMsg = "\nAgent moves forward... ...\nThe foul stench grew stronger... ...\nAgent was " + lol[randint(0, 4)] + " to death by Wumpus" 
            raise Exception(errMsg)
        if self.isConfundus(self.agent.getLocation()):
            sensorIndicators[0] = "on"
        if self.isStench(self.agent.getLocation()):
            sensorIndicators[1] = "on"
        if self.isTingle(self.agent.getLocation()):
            sensorIndicators[2] = "on"
        if self.isGlitter(self.agent.getLocation()):
            sensorIndicators[3] = "on"
        if self.isWall(self.agent.getLocation()):
            sensorIndicators[4] = "on"

        if(isShooting):
            if self.isWumpusInLineOfSight():
                sensorIndicators[5] = "on"
        return sensorIndicators

    def isWumpusInLineOfSight(self):
        current_direction = self.agent.getDirection()
        current_coords = self.agent.getLocation()
        if current_direction == current_direction.North or \
            current_direction == current_direction.South:
            deltaY = current_direction.value[1][1]
            i = current_coords.y # check y axis
            while(i <= MAX_VALID_ROW and i >= MIN_VALID_ROW):
                if self.isWumpus(Coordinate(current_coords.x, i)):
                    return True
                i += deltaY
        else:
            deltaX = current_direction.value[1][0]
            i = current_coords.x # check x axis
            while(i <= MAX_VALID_COL and i >= MIN_VALID_COL):
                if self.isWumpus(Coordinate(current_coords.y, i)):
                    return True
                i += deltaX
        return False

    def removeGoldAtCurrLoc(self, c):
        if c in self.golds:
            self.golds.remove(c)

    def moveAgentToRandSafeLocation(self): # Due to steeping into confundus portal
        if self.wumpus is None: # Killed by arrow, respawnable spot now
            self.mapBuilder.wumpus = None
        self.mapBuilder.golds = self.golds # Update any gold coins picked up, also respawnable spot now

        self.mapBuilder.gen_agent() # regenerate new agent...
        self.agent = self.mapBuilder.agent
        
    def removeWumpus(self):
        self.wumpus = None

    def removeGold(self, c):
        self.golds.remove(c)

    def isHome(self, c):
        return c == self.home

    def isGold(self, c):
        return c in self.golds

    def isWumpus(self, c):
        if self.wumpus is None: return False
        return c == self.wumpus

    def isConfundus(self, c):
        return c in self.confunduses
    
    def isWall(self, c):
        return c in self.walls

    def isAgent(self, c):
        return self.agent.getLocation() == c

    def isStench(self, c):
        return self.isWumpus(Coordinate(c.x-1, c.y)) or\
            self.isWumpus(Coordinate(c.x+1, c.y)) or\
            self.isWumpus(Coordinate(c.x, c.y+1)) or\
            self.isWumpus(Coordinate(c.x, c.y-1))

    def isTingle(self, c):
        return self.isConfundus(Coordinate(c.x-1, c.y)) or\
            self.isConfundus(Coordinate(c.x+1, c.y)) or\
            self.isConfundus(Coordinate(c.x, c.y+1)) or\
            self.isConfundus(Coordinate(c.x, c.y-1))
        
    def isGlitter(self, c):
        return self.isGold(c)

    def printGeneratedScenario(self):
        if(self.home is not None):
            print("Agent was generated at:", self.agent.location, "with", self.agent.getDirection())
            print("Therefore, home is at:", self.home)
            print("Gold was generated at:")
            for g in self.golds:
                print("(" + str(g.x) + "," + str(g.y) + ")")
            print("Wumpus was generated at:", self.wumpus)
            print("Confunduses was generated at:")
            for c in self.confunduses:
                print("(" + str(c.x) + "," + str(c.y) + ")", end=" ")
            print()

    '''
        loop by row first
        then loop by individual column
        
        ### ### ### ### ### ###     printOneCellForOneLine()
        ### ### ### ### ### ###     printOneCellForOneLine()
        ### ### ### ### ### ###     printOneCellForOneLine()
                                    print()
        ### ..T %.. ..T .=. ###
        ### ... -O- ... ... ###
        ### ... ... ... *.. ###

        ### ... ..T .=T ... ###
        ### ... ... ... -W- ###
        ### ... ... ... ... ###

        ### ... ..T %.. .=T ###
        ### ... -V- -O- ... ###
        ### ... ... ... ... ###

        ### ... ... ..T %.. ###
        ### ... ... ... -O- ###
        ### ... ... ... ... ###

        ### ... ... ... ..T ###
        ### ... ... ... ... ###
        ### ... ... ... ... ###

        ### ### ### ### ### ###
        ### ### ### ### ### ###
        ### ### ### ### ### ###
    '''
    def printAbsoluteMap(self):
        print("Absolute Map")

        # Row by Row first
        for r in range(MAX_ROW, -1, -1):
            # for each column, print each cell
            for count in range(3):
                # each cell has to be printed 3 times
                for c in range(MAX_COL+1):
                    cell_coord = Coordinate(c, r)
                    self.printOneCellForOneLine(cell_coord, count)
                if count == 1:
                    print(" " + str(r), end="")
                print()
            print()
        print("0   1   2   3   4   5") 

    '''
        Each map cell has the following structure in dots:
            ... - count 0
            ... - count 1
            ... - count 2
        - Reset to 0 when count becomes 3
    '''
    def printOneCellForOneLine(self, cell_coord, count):
        str_to_print = list("...")
        if count == 0: # first row of each cell
            if self.isWall(cell_coord): 
                str_to_print = "###"
            else:
                if self.isConfundus(cell_coord): 
                    str_to_print[0] = "%"
                if self.isStench(cell_coord):
                    str_to_print[1] = "="
                if self.isTingle(cell_coord):
                    str_to_print[2] = "T"
        elif count == 1: # second row of each cell
            if self.isWall(cell_coord): 
                str_to_print = "###"
            else:
                if self.isConfundus(cell_coord):
                    str_to_print = list("-O-")
                elif self.isWumpus(cell_coord):
                    str_to_print = list("-W-")
                elif self.isAgent(cell_coord):
                    str_to_print = list("---")
                    if self.agent.getDirection() == Direction.North:
                        str_to_print[1] = "^"
                    elif self.agent.getDirection() == Direction.East:
                        str_to_print[1] = ">"
                    elif self.agent.getDirection() == Direction.South:
                        str_to_print[1] = "v"
                    elif self.agent.getDirection() == Direction.West:
                        str_to_print[1] = "<"

        elif count == 2: # third row of each cell
            # str_to_print = str(cell_coord.x) + "," + str(cell_coord.y)
            if self.isWall(cell_coord): 
                str_to_print = "###"
            else:
                if self.isGold(cell_coord):
                    str_to_print[0] = "*"
                
        else:
            print("Something went terribly wrong!")
        print("".join(str_to_print), end=" ")


class RelativeMap:
    max_num_of_rows = 3
    max_num_of_cols = 3

    '''
        "Blind" Agent starts at relative (0, 0) and relative North
        [Confounded, Stench, Tingle, Glitter, Bump, Scream]
    '''
    def __init__(self) -> None:
        self.agent = Agent(Coordinate(0, 0), Direction.North)
        self.visited = [Coordinate(0, 0)] # print capital "S"
        # self.sensor_indicators_by_coord = {} # dictionary 
        self.tingles = []
        # self.glitters = []
        self.stenches = []
        self.coords_reasoned_to_be_safe = [] # print lowercase "s" 
        self.possible_wumpus_coords = [] # print "W"
        self.possible_confundus_coords = [] # print "O"
        self.known_walls = [] # update this after detecting Bump

    def updateStateBasedOnPrologAgent(self):
        self.visited = self.agent.getReasonedNpcOrSenseByName("visited")
        self.possible_wumpus_coords = self.agent.getReasonedNpcOrSenseByName("wumpus")
        self.possible_confundus_coords = self.agent.getReasonedNpcOrSenseByName("confundus")
        self.tingles = self.agent.getReasonedNpcOrSenseByName("tingle")
        # self.glitters = self.agent.getReasonedNpcOrSenseByName("glitter")
        self.stenches = self.agent.getReasonedNpcOrSenseByName("stench")
        self.coords_reasoned_to_be_safe = self.agent.getReasonedNpcOrSenseByName("safe")
        self.known_walls = self.agent.getReasonedNpcOrSenseByName("wall")


    def resetMaxRowsCols(self):
        self.max_num_of_rows = 3
        self.max_num_of_cols = 3


    def printMoves(self, moves):
        print("\n-----------Action Sequence----------")
        print(*moves, sep=", ")
        # for i in range(0, len(moves)):
        #     print(str(moves[) , end="")

    def printPercepts(self, sensorIndicators):
        percepts_str = "\n"
        percepts_str += "Confounded-" if sensorIndicators[0] == "on" else "C-"
        percepts_str += "Stench-" if sensorIndicators[1] == "on" else "S-"
        percepts_str += "Tingle-" if sensorIndicators[2] == "on" else "T-"
        percepts_str += "Glitter-" if sensorIndicators[3] == "on" else "G-"
        percepts_str += "Bump-" if sensorIndicators[4] == "on" else "B-"
        percepts_str += "Scream-" if sensorIndicators[5] == "on" else "S-"
        print(percepts_str)

    '''
        prints relative map based on location and direction of instance's agent
        and by
        Agent's reasoning and sensor indicators
    '''
    def printRelativeMap(self, sensorIndicators):
        self.updateStateBasedOnPrologAgent()
        agent_r_loc = self.agent.getLocation()

        self.max_num_of_rows = max((2 * abs(agent_r_loc.y)) + 3, self.max_num_of_rows)
        self.max_num_of_cols = max((2 * abs(agent_r_loc.x)) + 3, self.max_num_of_cols)

        max_x_coord = int(self.max_num_of_cols / 2) # max of 3 rows is 1, 5 is 2, 7 is 3
        max_y_coord = int(self.max_num_of_rows / 2)

        min_x_coord = max_x_coord * -1
        min_y_coord = max_y_coord * -1

        # print("min_x_coord", min_x_coord)
        # print("max_x_coord", max_x_coord)
        # print("min_y_coord", min_y_coord)
        # print("max_y_coord",max_y_coord)
        
        # Row by Row first
        for r in range(max_y_coord, min_y_coord-1, -1):
            # for each column, print each cell
            for count in range(3):
                # each cell has to be printed 3 times
                for c in range(min_x_coord, max_x_coord+1, 1):
                    cell_coord = Coordinate(c, r)
                    self.printOneCellForOneLine(cell_coord, count, sensorIndicators)
                if count == 1:
                    print(" " + str(r), end="") # Y-Axis Label
                print()
            print()
        for x in range(min_x_coord, max_x_coord+1, 1): print(str(x).ljust(4), end="") # X-Axis Label
        print()


    def printOneCellForOneLine(self, cell_coord, count, sensorIndicators):
        str_to_print = list("...")
        if count == 0: 
            if cell_coord in self.known_walls:
                str_to_print = "###"
            else:
                if cell_coord == self.agent.getLocation() and sensorIndicators[0] == "on": # confunded
                    str_to_print[0] = "%"
                if cell_coord in self.stenches:
                    str_to_print[1] = "=" 
                if cell_coord in self.tingles == True: # Tingle
                    str_to_print[2] = "T" 

        elif count == 1:
            str_to_print = list(" ? ")
            if cell_coord in self.known_walls:
                str_to_print = "###"

            else:
                if cell_coord == self.agent.getLocation(): # agent relative position
                    str_to_print = list("---")
                    if self.agent.getDirection() == Direction.North:
                        str_to_print[1] = "^"
                    elif self.agent.getDirection() == Direction.East:
                        str_to_print[1] = ">"
                    elif self.agent.getDirection() == Direction.South:
                        str_to_print[1] = "v"
                    elif self.agent.getDirection() == Direction.West:
                        str_to_print[1] = "<"
                elif cell_coord in self.visited:
                    str_to_print = " S "
                elif cell_coord in self.coords_reasoned_to_be_safe:
                    str_to_print = " s "
                elif cell_coord in self.possible_confundus_coords and\
                    cell_coord in self.possible_wumpus_coords:
                    str_to_print = "-U-"
                elif cell_coord in self.possible_wumpus_coords:
                    str_to_print = "-W-"
                elif cell_coord in self.possible_confundus_coords:
                    str_to_print = "-O-"
            
        elif count == 2:
            str_to_print = list("...")
            
            if cell_coord in self.known_walls:
                str_to_print = "###"

            else:
                if sensorIndicators[3] == True: # Glitter detected
                    str_to_print[0] = "*"
                if sensorIndicators[4] == True: # Bump detected
                    str_to_print[1] = "B"
                if sensorIndicators[5] == True: # Scream detected
                    str_to_print[2] = "@"
            
            # str_to_print = str(cell_coord.x) + "," + str(cell_coord.y)
        print("".join(str_to_print), end=" ")


    '''
        Driver would have known whether there is wall/confundus/wumpus ahead
        by calling absolute_map.isWall(), isAgent(), isStench(), etc
        If safe, 
            r_map.agent.moveforward() or turnright() or turnleft() or shoot(), etc
        Else,
            stay at same spot 

        y   rows (same for x/columns)
        0   3   
        1   5
        2   7
        3   9
        4   11

        Size of map is related by these equations:
            rows = 2y + 3
            columns = 2x + 3
    '''

def print_debug_message(move, abs_map, r_map, sensorIndicators):
    print("\nDebug Messages:")
    print(move)
    print("abs_map agent moved to", abs_map.agent.getLocation(), abs_map.agent.getDirection())
    print("r_map agent moved to", r_map.agent.getLocation(), r_map.agent.getDirection())
    print(sensorIndicators)

    

def main():
    isGameOver = False
    # isGameOver = 0
    runDriver = "yes"
    prolog = Prolog()
    prolog.consult("prolog_agent/agent.pl")

    while runDriver.lower() in ["yes", "y"]:
        print("Starting Hunt the Wumpus...\n")

        abs_map = AbsoluteMap() # Generate Random Scenario in constructor
        abs_map.printGeneratedScenario()
        abs_map.printAbsoluteMap()

        r_map = RelativeMap()
        r_map.agent.setProlog(prolog)
        
        KBS = printer.KnownWorld(prolog_interface=prolog)
        

        # r_map.agent.rebornPrologAgent() # reset Prolog Agent with reborn/0

        print("====================================================== \n")

        sensorIndicators = abs_map.generateSensorIndicators()
        sensorIndicators[0] = "on"
        r_map.agent.executeReposition(sensorIndicators)
        print("Initial Relative Map: ")
        r_map.printPercepts(sensorIndicators)
        # r_map.printRelativeMap(sensorIndicators)
        KBS.update_world()
        KBS.print_map()

        # prolog.assertz("explore([moveforward])")

        while isGameOver is False:
        # while isGameOver != 2:
            print("Executing explore()")
            moves_from_explore = r_map.agent.explore()
            print("explore() finished")
            abs_map.printAbsoluteMap()
            r_map.printMoves(moves_from_explore)

            if len(moves_from_explore) == 0:
                print("moves_from_explore is empty, terminating game")
                isGameOver = True

            for move in moves_from_explore:
                if(move == "moveforward"):
                    abs_map.agent.moveForward()
                    r_map.agent.moveForward()

                elif(move == "turnright"):
                    abs_map.agent.turnRight()
                    r_map.agent.turnRight()

                elif(move == "turnleft"):
                    abs_map.agent.turnLeft()
                    r_map.agent.turnLeft()
                # elif(move == "shoot"):
                #     isShooting = True
                elif(move == "pickup"):
                    abs_map.removeGoldAtCurrLoc(abs_map.agent.getLocation()) # So if step into confundus, can respawn here

                try:
                    isShooting = (move == "shoot")
                    sensorIndicators = abs_map.generateSensorIndicators(isShooting)
                    if(sensorIndicators[0] == "on"): # Stepped into Confundus Portal
                        r_map.printPercepts(sensorIndicators) # Print
                        # r_map.printRelativeMap(sensorIndicators)
                        KBS.update_world()
                        KBS.print_map()
                        print("> Stepped into confundus portal, respawning in new, safe location")

                        abs_map.moveAgentToRandSafeLocation() # find new safe spawn spot
                        r_map.agent.resetAgent()
                        r_map.resetMaxRowsCols()
                        sensorIndicators = abs_map.generateSensorIndicators() # new sensor indicators at new coordinate
                        r_map.agent.executeReposition(sensorIndicators) # query prolog reposition(L) with new sensor inputs
                        

                        r_map.printPercepts(sensorIndicators) # Print again
                        # r_map.printRelativeMap(sensorIndicators)
                        # KBS.update_world()
                        # KBS.print_map()
                        break

                    if(sensorIndicators[4] == "on"): # if move forward and bump into wall
                        abs_map.agent.setLocation(abs_map.agent.prevLocation)
                        r_map.agent.setLocation(r_map.agent.prevLocation)
                    
                    if sensorIndicators[5] == "on":
                        abs_map.removeWumpus() # So if step into confundus, can respawn here
                        r_map.agent.setKilledWumpus()

                    if move == "shoot" and sensorIndicators[5] == "off":
                        r_map.agent.setMissedWumpus()

                    r_map.agent.executeMove(move, sensorIndicators)
                    print("\n")
                    r_map.printPercepts(sensorIndicators)
                    # r_map.printRelativeMap(sensorIndicators)
                    KBS.update_world()
                    KBS.print_map()

                    # input("\nContinue?")
                    # print_debug_message(move, abs_map, r_map, sensorIndicators)
                except Exception as error:
                    # r_map.agent.rebornPrologAgent() # reset prolog map
                    # abs_map = AbsoluteMap()     # reset absolute map for next round
                    print(error)
                    # print(traceback.format_exc())
                    print("Game Over!", "\n")
                    isGameOver = True # break while loop
                    break # break for loop
            
            # TODO how to terminate game?
            # isGameOver = True
            # isGameOver += 1

        print("\n\nGame Over! Hunt the Wumpus finished.")
        exit(0)
        # runDriver = input("Enter (Y/n) to continue another round: ")
        # if runDriver.lower() not in ["yes", "y"]: print("Exiting program...")


if __name__ == '__main__':
    main()

