import unittest

from entities.Driver import Driver
from helpers.Constants import *
from map_functions.map_generator import map_generator


class DriverTest(unittest.TestCase):

    def setUp(self) -> None:
        position = [0, 0]
        direction = Directions.R_NORTH
        world_map = map_generator()
        self.d = Driver(position, direction, world_map)

    # Unit Tests for movement
    def test_driver(self):
        self.assert_(self.d.print(), Directions.R_NORTH)

    def test_no_movement(self):
        action_list = []
        self.d.move(action_list)

    def test_forward_movement(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD]
        self.d.move(action_list)
        # print(self.d.position)
        self.assert_(self.d.position == [0, 3], True)

    def test_right_movement(self):
        # print(self.d.print_map())
        action_list = [Instructions.TURN_LEFT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD]
        self.d.move(action_list)
        # print(self.d.position)
        self.assert_(self.d.position == [2, 0], True)

    def test_bump_movement(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD]
        perceptionsList = self.d.move(action_list)
        # should detect a glitter at this position
        # print(self.d.position)
        self.assert_(self.d.position == [0, 5], True)
        self.assert_('B' in perceptionsList, True)

    # Unit Tests for gold pickup
    def test_invalid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.PICKUP]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 0, True)

    def test_valid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.TURN_LEFT,
                       Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.PICKUP]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 1, True)

    # Unit Tests for Wumpus Shooting
    def test_north_wumpus_destruction(self):
        action_list = [Instructions.TURN_LEFT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.TURN_RIGHT, Instructions.SHOOT]
        perceptionList = self.d.move(action_list)
        self.assert_("@" in perceptionList, True)

    def test_north_wumpus_destruction_fail(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.TURN_LEFT,
                       Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.TURN_RIGHT, Instructions.SHOOT]
        self.d.move(action_list)
        perceptionList = self.d.move(action_list)
        self.assert_("@" not in perceptionList, True)

    def test_south_wumpus_destruction(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.TURN_LEFT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.TURN_LEFT, Instructions.SHOOT]
        perceptionList = self.d.move(action_list)
        self.assert_("@" in perceptionList, True)

    def test_east_wumpus_destruction(self):
        action_list = [Instructions.TURN_LEFT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.TURN_RIGHT, Instructions.MOVE_FORWARD,
                       Instructions.TURN_RIGHT, Instructions.MOVE_FORWARD, Instructions.SHOOT]
        # action_list = [Instructions.TURN_LEFT]
        perceptionList = self.d.move(action_list)
        self.assert_("@" in perceptionList, True)

    def test_west_wumpus_destruction(self):
        action_list = [Instructions.MOVE_FORWARD, Instructions.TURN_LEFT,
                       Instructions.MOVE_FORWARD, Instructions.SHOOT]
        perceptionList = self.d.move(action_list)
        self.assert_("@" in perceptionList, True)

    """
    TODO : 
        1. Test where agent faces a wall and tries to shoot at the wall <- Edge Case
        2. Test where agent misses a wumpus
            -> Right now, we test by reducing n
    """

    def test_step_on_wumpus(self):
        action_list = [Instructions.TURN_LEFT, Instructions.MOVE_FORWARD, Instructions.MOVE_FORWARD,
                       Instructions.MOVE_FORWARD, Instructions.TURN_RIGHT, Instructions.MOVE_FORWARD]
        with self.assertRaises(SystemExit) as cm:
            self.d.move(action_list)
        self.assertEqual(cm.exception.code, 1)


if (__name__ == "__main__"):
    unittest.main()
