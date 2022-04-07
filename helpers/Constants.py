from enum import Enum


class Directions(Enum):
    R_NORTH = "RNorth"
    R_SOUTH = "RSouth"
    R_EAST = "REast"
    R_WEST = "RWest"


class Instructions(Enum):
    MOVE_FORWARD = "moveforward"
    TURN_RIGHT = "turnright"
    TURN_LEFT = "turnleft"
    PICKUP = "pickup"
    SHOOT = "shoot"
