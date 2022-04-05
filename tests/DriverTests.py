from entities.Driver import Driver
from map_functions.map_generator import map_generator
import unittest
from helpers.Constants import *

class DriverTest(unittest.TestCase):

    def setUp(self) -> None:
        position = [0,0]
        direction = Directions.RNorth
        world_map = map_generator()
        self.d = Driver(position, direction, world_map)

    def test_driver(self):
        self.assert_(self.d.print(), Directions.RNorth)

    def test_no_movement(self):
        action_list = []
        self.d.move(action_list)

    def test_forward_movement(self):
        action_list = [Instructions.MOVE_FORWARD,Instructions.MOVE_FORWARD,Instructions.MOVE_FORWARD]
        self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position==[0,3], True)

    def test_right_movement(self):
        action_list = [Instructions.TURN_RIGHT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD]
        self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position==[2,0], True)

    def test_bump_movement(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD]
        perceptionsList = self.d.move(action_list)
        # should detect a glitter at this position
        print(self.d.position)
        self.assert_(self.d.position == [0,5], True)
        self.assert_('B' in perceptionsList, True)

    def test_invalid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.PICKUP]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 0, True)

    def test_valid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.TURN_RIGHT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.PICKUP]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 1, True)

if (__name__ == "__main__"):
    unittest.main()