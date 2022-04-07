import unittest

from entities.Driver import Driver
from helpers.Constants import *
from map_functions.map_generator import map_generator


class DriverTest(unittest.TestCase):

    def setUp(self) -> None:
        position = [0, 0]
        direction = Directions.R_NORTH.value
        world_map = map_generator("../map.pl")
        self.d = Driver(position, direction, world_map)

    # Unit Tests for movement
    def test_driver(self):
        self.assert_(self.d.position, Directions.R_NORTH.value)

    def test_no_movement(self):
        action_list = []
        self.d.move(action_list)

    def test_forward_movement(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value]
        self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position == [0, 3], True)

    def test_right_movement(self):
        # print(self.d.print_map())
        action_list = [Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value]
        self.d.move(action_list)
        # print(self.d.position)
        self.assert_(self.d.position == [2, 0], True)

    def test_bump_movement(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value]
        perceptionsList = self.d.move(action_list)
        print(self.d.position)
        self.assert_(self.d.position == [0, 5], True)
        # TODO assert the correct on inside perceptionlist instead of 'B'
        # self.assert_('B' in perceptionsList, True)

    # Unit Tests for gold pickup
    def test_invalid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.PICKUP.value]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 0, True)

    def test_valid_pickup_gold(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value,
                       Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.PICKUP.value]
        perceptionList = self.d.move(action_list)
        self.assert_(self.d.coins == 1, True)

    # Unit Tests for Wumpus Shooting
    def test_north_wumpus_destruction(self):
        action_list = [Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.TURN_RIGHT.value, Instructions.SHOOT.value]
        perceptionList = self.d.move(action_list)
        # TODO assert the correct on inside perceptionlist instead of '@'
        # self.assert_("@" in perceptionList, True)

    def test_north_wumpus_destruction_fail(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value,
                       Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.TURN_RIGHT.value, Instructions.SHOOT.value]
        self.d.move(action_list)
        perceptionList = self.d.move(action_list)
        # TODO assert the correct on inside perceptionlist instead of '@'
        # self.assert_("@" not in perceptionList, True)

    def test_south_wumpus_destruction(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value, Instructions.SHOOT.value]
        perceptionList = self.d.move(action_list)
        # TODO assert the correct on inside perceptionlist instead of '@'
        # self.assert_("@" in perceptionList, True)

    def test_east_wumpus_destruction(self):
        action_list = [Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.TURN_RIGHT.value, Instructions.MOVE_FORWARD.value,
                       Instructions.TURN_RIGHT.value, Instructions.MOVE_FORWARD.value, Instructions.SHOOT.value]
        # action_list = [Instructions.TURN_LEFT.value]
        perceptionList = self.d.move(action_list)
        # TODO assert the correct on inside perceptionlist instead of '@'
        # self.assert_("@" in perceptionList, True)

    def test_west_wumpus_destruction(self):
        action_list = [Instructions.MOVE_FORWARD.value, Instructions.TURN_LEFT.value,
                       Instructions.MOVE_FORWARD.value, Instructions.SHOOT.value]
        perceptionList = self.d.move(action_list)
        # TODO assert the correct on inside perceptionlist instead of '@'
        # self.assert_("@" in perceptionList, True)

    """
    TODO : 
        1. Test where agent faces a wall and tries to shoot at the wall <- Edge Case
        2. Test where agent misses a wumpus
            -> Right now, we test by reducing n
    """

    def test_step_on_wumpus(self):
        action_list = [Instructions.TURN_LEFT.value, Instructions.MOVE_FORWARD.value, Instructions.MOVE_FORWARD.value,
                       Instructions.MOVE_FORWARD.value, Instructions.TURN_RIGHT.value, Instructions.MOVE_FORWARD.value]
        with self.assertRaises(SystemExit) as cm:
            self.d.move(action_list)
        self.assertEqual(cm.exception.code, 1)


    # Test Maximum move count
    def test_max_moves(self):
        action_list = [Instructions.TURN_LEFT.value]
        with self.assertRaises(SystemExit) as cm:
            for i in range (0,52):
                self.d.move(action_list)

        self.assertEqual(cm.exception.code, 1)



if (__name__ == "__main__"):
    unittest.main()
