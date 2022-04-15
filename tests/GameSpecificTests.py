import unittest

from entities.Driver import Driver
from helpers.Constants import *
from map_functions.map_generator import *


class GameSpecificTest(unittest.TestCase):
    def setUp(self) -> None:
        position = [0, 0]
        direction = Directions.R_NORTH.value
        world_map = map_generator_legacy("../map.pl")
        self.d = Driver(position, direction, world_map)

    def test_map_generator_legacy(self):
        world_map = map_generator_legacy("../map.pl")
        for i in range(0, len(world_map)):
            # prints each row
            print(world_map[i])
        self.assert_(len(world_map) == 6)
        self.assert_(len(world_map[0]) == 7)

    def test_map_generator(self):
        wumpus_coords = [[4,2]]
        gold_coords = [[0,0]]
        portal_coords = [[0,5]]
        world_map = map_generator(wumpus_coords=wumpus_coords, gold_coords=gold_coords, portal_coords=portal_coords)
        for i in range(0, len(world_map)):
            # prints each row
            print(world_map[i])
        self.assert_(len(world_map) == 6)
        self.assert_(len(world_map[0]) == 7)


    def testCase1(self):
        print(self.d.position)
        action_list = [Instructions.TURN_LEFT.value]
        perceptionList = self.d.move(action_list)
        print(perceptionList)
        print(self.d.position)

    def testMultipleMoves(self):
        print(self.d.position)
        action_list = [Instructions.TURN_RIGHT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.TURN_LEFT.value, Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value, Instructions.TURN_LEFT.value]
        # action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value]
        perceptionList = self.d.move(action_list)
        # print(perceptionList)
        print(len(action_list))
        print(len(perceptionList))
        print(self.d.position)
