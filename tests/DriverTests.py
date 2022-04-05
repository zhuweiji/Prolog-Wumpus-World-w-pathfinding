from entities.Driver import Driver
from map_functions.map_generator import map_generator
import unittest

class DriverTest(unittest.TestCase):

    def setUp(self) -> None:
        position = [0,0]
        direction = "RNorth"
        world_map = map_generator()
        self.d = Driver(position, direction, world_map)

    def test_driver(self):
        self.assert_(self.d.print(), "RNorth")

    def test_no_movement(self):
        action_list = []
        self.d.move(action_list)

    def test_forward_movement(self):
        action_list = ["moveforward","moveforward","moveforward"]
        self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position==[0,3], True)

    def test_right_movement(self):
        action_list = ["turnright", "moveforward", "moveforward"]
        self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position==[2,0], True)

    def test_bump_movement(self):
        action_list = ["moveforward", "moveforward", "moveforward", "moveforward", "moveforward", "moveforward", "moveforward", "moveforward", "moveforward"]
        perceptionsList = self.d.move(action_list)
        # should detect a glitter at this position
        print(self.d.position)
        self.assert_(self.d.position == [0,5], True)
        self.assert_('B' in perceptionsList, True)

    def test_invalid_pickup_gold(self):
        action_list = ["moveforward", "pickup"]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 0, True)

    def test_valid_pickup_gold(self):
        action_list = ["moveforward", "moveforward", "turnright", "moveforward", "moveforward", "pickup"]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 1, True)

if (__name__ == "__main__"):
    unittest.main()