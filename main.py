from pyswip import Prolog
from entities import Driver
from helpers.Constants import *
from map_functions.map_generator import map_generator
import time

if (__name__ == "__main__"):
    prolog = Prolog()
    prolog.consult("prolog_agent/agent.pl")

    position = [0, 0]
    direction = Directions.R_NORTH.value
    world_map = map_generator("map.pl")
    d = Driver.Driver(position, direction, world_map)


    while (d.current_move_count < d.MAX_MOVES):
        move_list = []

        for soln in prolog.query("explore(L)"):
            # print(type(soln["L"][-1]))
            # print(type(soln["L"][0]))
            endIndex = len(soln["L"]) - 1
            move_list = soln["L"][0:endIndex]
            print(soln["L"])
            if (type(soln["L"][-1]) == str):
                move_list.append(soln["L"][-1])
            print(f"Suggested Move List : {move_list}")

        # print(move_list)
        CompoundListOfPerceptionStrings = d.move(move_list)
        # print("Built Perception: " , end = "\t")
        # print(build_perception)

        print(f"Executed Move List : {move_list}")
        print(f"Driver Position : {d.position}")

        for i in range (0, len(move_list)):
            instruction = f"move({move_list[i]},{CompoundListOfPerceptionStrings[i]})"
            print(f"Agent Instruction:\t {instruction}")
            result = list(prolog.query(instruction))
            # print(f"Result : {result}")
            print()

        time.sleep(0.1)

