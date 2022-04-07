from helpers import config
from helpers import Constants
import sys

class Driver:
    def __init__(self, position, direction, world_map) -> None:
        self.position = position
        self.direction = direction
        self.directionList = [Constants.Directions.R_NORTH.value, Constants.Directions.R_EAST.value, Constants.Directions.R_SOUTH.value,
                              Constants.Directions.R_WEST.value]
        self.world_map = world_map
        self.coins = 0
        self.arrow = 1
        self.percepts = []
        self.MAX_MOVES = 50
        self.current_move_count = 0

    def shoot(self):
        self.arrow -= 1
        return

    def pickup(self):
        self.coins += 1
        return

    def move(self, instructionList):

        perceptionList = []

        for instruction in instructionList:

            if (self.current_move_count >= self.MAX_MOVES):
                sys.exit(1)

            if (instruction == Constants.Instructions.TURN_LEFT.value):
                """
                self.directionList = [Constants.Directions.R_NORTH, Constants.Directions.R_EAST, Constants.Directions.R_SOUTH,
                              Constants.Directions.R_WEST]
                """
                if (self.direction == self.directionList[0]):
                    self.direction = self.directionList[3]
                elif (self.direction == self.directionList[1]):
                    self.direction = self.directionList[0]
                elif (self.direction == self.directionList[2]):
                    self.direction = self.directionList[1]
                else:
                    self.direction = self.directionList[2]

            elif (instruction == Constants.Instructions.TURN_RIGHT.value):
                if (self.direction == self.directionList[0]):
                    self.direction = self.directionList[1]
                elif (self.direction == self.directionList[1]):
                    self.direction = self.directionList[2]
                elif (self.direction == self.directionList[2]):
                    self.direction = self.directionList[3]
                else:
                    self.direction = self.directionList[0]

            # TODO : Check for collisions
            elif (instruction == Constants.Instructions.MOVE_FORWARD.value):
                curr_x = self.position[0]
                curr_y = self.position[1]
                """
                self.directionList = [Constants.Directions.R_NORTH, Constants.Directions.R_EAST, Constants.Directions.R_SOUTH,
                              Constants.Directions.R_WEST]
                """
                if (self.direction == self.directionList[0]):
                    # move upwards
                    new_position = [curr_x, curr_y + 1]
                elif (self.direction == self.directionList[1]):
                    # move right
                    new_position = [curr_x - 1, curr_y]
                elif (self.direction == self.directionList[2]):
                    # move downwards
                    new_position = [curr_x, curr_y - 1]
                else:
                    # move left
                    new_position = [curr_x + 1, curr_y]

                # print(f"Current Position : {[curr_x, curr_y]}")
                # print(f"New Position : {new_position}")

                boolean_bump = self.wall_check(new_position)
                if not boolean_bump:
                    self.position = new_position
                else:
                    print("Bump found")
                    perceptionList.append('B')
                    break

            elif (instruction == Constants.Instructions.PICKUP.value):
                # sanity check : Check if coin exists
                curr_x = self.position[0]
                curr_y = self.position[1]
                position_perception = self.world_map[curr_y][curr_x]
                if '*' in position_perception:
                    # print("Found Coin")
                    self.pickup()
                # else:
                    # print("Invalid pickup instruction")

            elif (instruction == Constants.Instructions.SHOOT.value):
                # TODO check if there is any wumpus ahead
                self.shoot()
                if (self.wumpus_check()):
                    perceptionList.append("@")

            # check for death condition
            if "W" in self.world_map[self.position[1]][self.position[0]]:
                # print("Landed on WUMPUS")
                # TODO check if we want to raise an exception here
                # raise exit error code 1 for unit test purposes
                # any integer from 0-255 should be fine
                # TODO Determine what the different exit codes represent, if anything
                sys.exit(1)

            self.current_move_count += 1

        curr_x = self.position[0]
        curr_y = self.position[1]

        self.world_map[curr_y][curr_x] += "-"
        self.print_map()
        self.world_map[curr_y][curr_x] = self.world_map[curr_y][curr_x].replace("-", "")

        # check final position for percepts
        self.percepts = self.world_map[curr_y][curr_x]
        for perception in perceptionList:
            self.percepts += perception
        built_perception = self.perception_builder()
        return built_perception

    def wall_check(self, position):
        x, y = position[0], position[1]
        max_x, max_y = config.MAP_SIZE
        if (x < 0 or x >= max_x or y < 0 or y >= max_y):
            return True

        return False

    def wumpus_check(self) -> bool:

        current_x = self.position[0]
        current_y = self.position[1]
        max_x, max_y = config.MAP_SIZE

        # Case 1 : R_North
        if (self.direction == Constants.Directions.R_NORTH.value):
            for i in range(current_y + 1, max_y):
                perceptsList = self.world_map[i][current_x]
                if "W" in perceptsList:
                    # print("WUMPUS SHOT")
                    return True

        elif (self.direction == Constants.Directions.R_SOUTH.value):
            for i in range(0, current_y):
                perceptsList = self.world_map[i][current_x]
                if "W" in perceptsList:
                    # print("WUMPUS SHOT")
                    return True

        elif (self.direction == Constants.Directions.R_EAST.value):
            i = self.world_map[current_y]
            for j in range(0, current_x):
                perceptsList = i[j]
                if "W" in perceptsList:
                    # print("WUMPUS SHOT")
                    return True

        elif (self.direction == Constants.Directions.R_WEST.value):
            i = self.world_map[current_y]
            for j in range(current_x + 1, max_x):
                perceptsList = i[j]
                if "W" in perceptsList:
                    # print("WUMPUS SHOT")
                    return True

    def perception_builder(self):
        # Confounded, Stench, Tingle, Glitter, Bump, Scream
        confounded = "off"
        stench = "off"
        tingle = "off"
        glitter = "off"
        bump = "off"
        scream = "off"
        for perception in self.percepts:
            # print(f"self.percepts : {self.percepts}")
            if (perception == "="):
                # stench found
                stench = "on"
            elif (perception == "*"):
                # glitter found
                glitter = "on"
            elif (perception == "T"):
                # tingle from nearby portal
                tingle = "on"
            elif (perception == "O"):
                print("Found confounded")
                # stepped on portal
                confounded = "on"
            elif (perception == "B"):
                # bumped into wall
                bump = "on"
            elif (perception == "@"):
                # scream heard
                scream = "on"
        result = confounded +  "," +  stench  + "," + tingle  + "," +  glitter  + "," +  bump  + "," +  scream
        return result

    def print_map(self):
        x, y = config.MAP_SIZE
        for i in range(0, y):
            for j in range(0, x):
                print(self.world_map[i][j], end="\t")
            print()


def rightof(direction):
    getvalue = lambda x: Constants.Directions[x].value
    
    if direction == getvalue('R_NORTH'):
        return getvalue('R_EAST')