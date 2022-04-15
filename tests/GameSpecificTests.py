import unittest

from entities.Driver import Driver
from helpers.Constants import *
from map_functions.map_generator import map_generator

class GameSpecificTest(unittest.TestCase):
    def setUp(self) -> None:
        position = [0, 0]
        direction = Directions.R_NORTH.value
        world_map = map_generator("../map.pl")
        self.d = Driver(position, direction, world_map)

    def testCase1(self):
        print(self.d.position)
        action_list = [Instructions.TURN_LEFT.value]
        perceptionList = self.d.move(action_list)
        print(perceptionList)
        print(self.d.position)

    def testMultipleMoves(self):
        print(self.d.position)
        action_list = [Instructions.TURN_RIGHT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value, Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value, Instructions.TURN_LEFT.value]
        # action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value]
        perceptionList = self.d.move(action_list)
        # print(perceptionList)
        print(len(action_list))
        print(len(perceptionList))
        print(self.d.position)

