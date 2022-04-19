import unittest

from entities.Driver import Driver
from helpers.Constants import *
from map_functions.map_generator import *


class GameSpecificTest(unittest.TestCase):
    # def setUp(self) -> None:
    #     position = [0, 0]
    #     direction = Directions.R_NORTH.value
    #     world_map = map_generator_legacy("../map.pl")
    #     self.d = Driver(position, direction, world_map)

    def test_map_generator(self):
        position = [0, 0]
        direction = Directions.R_NORTH.value
        wumpus_coords = [[4, 2]]
        gold_coords = [[0, 0]]
        portal_coords = [[0, 5]]
        world_map = map_generator(wumpus_coords=wumpus_coords, gold_coords=gold_coords, portal_coords=portal_coords)
        self.d = Driver(position, direction, world_map)

        for i in range(0, len(world_map)):
            # prints each row
            print(world_map[i])
        self.assert_(len(world_map) == 6)
        self.assert_(len(world_map[0]) == 7)

    def testCase1(self):
        position = [0, 0]
        direction = Directions.R_NORTH.value
        wumpus_coords = [[4, 2]]
        gold_coords = [[0, 0]]
        portal_coords = [[0, 5]]
        world_map = map_generator(wumpus_coords=wumpus_coords, gold_coords=gold_coords, portal_coords=portal_coords)
        self.d = Driver(position, direction, world_map)

        print(self.d.position)
        action_list = [Instructions.TURN_LEFT.value]
        perceptionList = self.d.move(action_list)
        print(perceptionList)
        print(self.d.position)

    # TODO: Create game specific tests
    # TODO: Determine what to test for each game
    def test_game_1(self):
        return
