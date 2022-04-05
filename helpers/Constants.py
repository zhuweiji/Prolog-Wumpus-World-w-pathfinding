from enum import Enum

class Directions(Enum):
    RNorth = "RNorth"
    RSouth = "RSouth"
    REast = "REast"
    RWest = "RWest"

class Instructions(Enum):
    MOVE_FORWARD = "moveforward"
    TURN_RIGHT = "turnright"
    TURN_LEFT = "turnleft"
    PICKUP = "pickup"