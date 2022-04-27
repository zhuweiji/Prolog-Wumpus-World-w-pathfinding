from pyswip import Prolog
from entities import Driver
from helpers.Constants import *
from map_functions.map_generator import map_generator

from prolog_agent import printer

if (__name__ == "__main__"):
    prolog = Prolog()
    prolog.consult("prolog_agent/agent.pl")

    KBS = printer.KnownWorld(prolog_interface=prolog)
    
    position = [0, 0]
    direction = Directions.R_NORTH.value

    wumpus_coords = [[4, 2]]
    gold_coords = [[2, 0]]
    portal_coords = [[0, 3]]
    world_map = map_generator(wumpus_coords=wumpus_coords, gold_coords=gold_coords, portal_coords=portal_coords)

    d = Driver.Driver(position, direction, world_map)

    prolog.query("reborn.")
    prolog.query("reposition([off,off,off,off,off,off]).")
    while (d.current_move_count < d.MAX_MOVES):
        move_list = []

        for soln in prolog.query("explore(L)"):
            endIndex = len(soln["L"]) - 1
            move_list = soln["L"][0:endIndex]

            if not soln['L']:
                print('explore(L) returned an empty list.')
                print('Game complete!')
                print(f'Collected {KBS.numGoldCoins} out of {len(gold_coords)} coins')
                exit(0)

            if (type(soln["L"][-1]) == str):
                move_list.append(soln["L"][-1])

        if (len(move_list)==0):
            break

        # print(f"Driver Position before movement: {d.position}")
        CompoundListOfPerceptionStrings = d.move(move_list)
        # print(f"Driver Position after  movement: {d.position}")

        # print(f"len(move_list) == len(CompoundListOfPerceptionStrings) = {len(move_list) == len(CompoundListOfPerceptionStrings)}")

        print(f"Driver: Move List : {move_list}")

        print(f"Driver : Built Perception: {CompoundListOfPerceptionStrings}")
        for i in range (0, len(move_list)):

            # print(f"Iteration : {i}")
            # print(f"move[{i}] : {move_list[i]}")
            # print(f"compound_perception[{i}]: {CompoundListOfPerceptionStrings[i]}")
            # print(f"type(compound_perception[{i}]): {type(CompoundListOfPerceptionStrings[i])}")

            instruction = f"move({move_list[i]},[{CompoundListOfPerceptionStrings[i]}])"
            # print(f"Agent Instruction:\t {instruction}")
            result = list(prolog.query(instruction))
            # print(f"Result : {result}")
            
        KBS.update_world()
        KBS.print_map()
        # time.sleep(0.5)