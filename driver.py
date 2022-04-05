from pyswip import Prolog
from driver.helpers import helper
from driver.map_functions.map_generator import map_generator

prolog = Prolog()
prolog.consult("driver.pl")

if (__name__ == "__main__"):
    # creates walls.pl with wall information
    helper.create_walls()
    world_map = map_generator()