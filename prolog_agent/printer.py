
from dataclasses import dataclass, field
import re
from pyswip import Prolog
import itertools
import os 
os.system("")

AXIS_SPACING = 3

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    
class KBSPrinterException(Exception): pass


@dataclass 
class PrologAgent:
    coordinates: tuple
    direction: str
    
    def update(self, coordinates, direction):
        self.coordinates = coordinates
        self.direction = direction
    
@dataclass 
class PrettyMap:
    _map: list
    
    def size(self):
        return len(self._map[0]), len(self._map)
    
    def prettyprint(self):
        prettify = lambda row: str(row).replace(',','').replace(']','').replace('[','').replace("'", '').replace('"','')

        def print_person_in_color(string):
            person = next((i for i in ['>','<','^','v'] if i in string), None)
            if person:
                split_strs = string.split(person)
                print(split_strs[0],end='')
                print(bcolors.OKGREEN + person + bcolors.ENDC, end='')
                print(split_strs[1])
            else:
                print(string)
                
        
        for row in self._map[::-1]:
            first_row = prettify([cell.row_1() for cell in row])
            middle_row = prettify([cell.row_2() for cell in row])
            third_row = prettify([cell.row_3() for cell in row])
            
            y_coords = row[0].coords[1]
            spacing_req = AXIS_SPACING - len(str(y_coords))-1
            
            
            print(f"{' '*AXIS_SPACING}| {first_row}")
            print_person_in_color(f"{y_coords} {' '*spacing_req}| {middle_row}")
            print(f"{' '*AXIS_SPACING}| {third_row}")
            print()
            
        last_row = self._map[::-1][-1]
        x_axis_print = ' '.join(f' {cell.coords[0]} ' for cell in last_row)
        print(' '*AXIS_SPACING, '-'*(len(x_axis_print)))
        print(f"{' '*AXIS_SPACING}  {x_axis_print}")
        # print([cell.coords for cell in row])
            
    
@dataclass
class KnownWorld:
    prolog_interface:  object
    agent:             PrologAgent = PrologAgent((0, 0), 'rnorth')
    visited:           list = field(default_factory=list)
    stench:            list = field(default_factory=list)
    tingle:            list = field(default_factory=list)
    wall:              list = field(default_factory=list)
    glitter:           list = field(default_factory=list)   
    possibleWumpus:    list = field(default_factory=list)
    possibleConfundus: list = field(default_factory=list)
    bump:              list = field(default_factory=list)
    
    scream:            bool = False
    safe:              bool = False
    wumpusAlive:       bool = True
    hasarrow:          bool = True
    numGoldCoins:      int  = 0
    
    home_agent: bool = False
    
    def __post_init__(self) -> None:
        if self.prolog_interface.query('printHunter.'):
            self.home_agent = True
        
    def print_map(self):
        rel_map = self.create_map()
        map = PrettyMap(rel_map)
        
        map.prettyprint()
        
    def create_map(self):       
        cells = {}
        for attribute_name, attribute_value in [(i,j) for i,j in self.__dict__.items() if i != 'prolog_interface']:
            if isinstance(attribute_value, list):
                for coords in attribute_value:
                    if coords not in cells: cells[coords] = MapCell(coords=coords) 
                    mapcell = cells[coords]
                    if attribute_name == 'visited': mapcell.visited = True
                    if attribute_name == 'stench': mapcell.stench = True
                    if attribute_name == 'tingle': mapcell.tingle = True
                    if attribute_name == 'wall': mapcell.wall = True
                    if attribute_name == 'possibleWumpus': mapcell.wumpus = True
                    if attribute_name == 'possibleConfundus': mapcell.portal = True
                    if attribute_name == 'safe': mapcell.safe = True
            
            elif attribute_name == 'agent':
                coords = attribute_value.coordinates
                print(f'agent coordinates: {coords}')
                if coords not in cells: cells[coords] = MapCell(coords=coords) 
                mapcell = cells[coords]
                mapcell.agent_direction = attribute_value.direction

                if self.__dict__['bump']: 
                    mapcell.bump = True
        
                if self.__dict__['scream']: 
                    mapcell.scream = True
        
        
        max_x,max_y, min_x, min_y = 0,0,0,0
        for mapcell in cells.values():
            coords = mapcell.coords
            if coords[0] > max_x: max_x = coords[0]
            if coords[1] > max_y: max_y = coords[1]
            if coords[0] < min_x: min_x = coords[0]
            if coords[1] < min_y: min_y = coords[1]
        
        # print(max_x, max_y, min_x, min_y)
        map = []
        for yidx in range(min_y, max_y+1):
            row = []
            for xidx in range(min_x, max_x+1):
                coords = (xidx, yidx)
                if coords in cells:
                    cell = cells[coords]
                else:
                    cell = MapCell(coords)
                    cells[coords] = cell
                row.append(cell)
            map.append(row)
        
        return map
                    
        
    def update_world(self):
        coords, direction = self.query_agent_coords()
        self.agent.update(coords, direction)
        
        self.visited = self.query_compound_coords("visited")
        self.stench = self.query_compound_coords("stench")
        self.tingle = self.query_compound_coords("tingle")
        self.wall = self.query_compound_coords("wall")
        self.safe = self.query_compound_coords("safe")
        
        
        self.possibleWumpus = self.query_compound_coords("possibleWumpus")
        self.possibleConfundus = self.query_compound_coords("possibleConfundus")
        
        self.wumpusAlive = self.query_bool('wumpusAlive')
        self.hasarrow = self.query_bool('hasarrow')
        self.bump = self.query_bool('justbumped')
        self.scream = self.query_bool('justscreamed')
        
        self.numGoldCoins = self.query_one_numeral('numGoldCoins')
        
    def restart_world(self):
        pass
    
    def query_agent_coords(self):
        res = self.query_first_solution(f"findall([X,Y,D], hunter(X,Y,D), Output).")
        if not res or not 'Output' in res: raise KBSPrinterException('Could not query agent coordinates')
        if not res['Output']: raise KBSPrinterException('Agent coordinates are empty')
        res = res['Output'][0]
        return ((int(res[0]), int(res[1])), res[2])
        
    def query_compound_coords(self, compound):
        res = self.query_first_solution(f"findall([X,Y], {compound}(X,Y), Output).")
        
        if not res or 'Output' not in res: raise KBSPrinterException(f'Could not query values of {compound} coordinates')
        return [tuple(int(j) for j in i) if isinstance(i, list) else i for i in res['Output']]
    
    def query_bool(self, compound):
        res = self.query_first_solution(f'{compound}(O).').get('O', None)
        if not res: raise KBSPrinterException(f'Could not query {compound} status')
        return res == 'true' 
    
    def query_one_numeral(self,compound):
        res = self.query_first_solution(f'{compound}(O).').get('O', None)
        if res != 0:
            if not res: raise KBSPrinterException(f'Could not query {compound} status')
        return res
            
                
    def query_first_solution(self, query):
        res = list(self.prolog_interface.query(query))
        if not res:
            return None
        return res[0]
    
@dataclass
class MapCell:
    coords:               tuple    = None
    agent_direction:      str = ''
    confounded:           bool    = False
    visited:              bool    = False
    stench:               bool    = False
    tingle:               bool    = False
    wall:                 bool    = False
    glitter:              bool    = False
    wumpus:               bool    = False
    portal:               bool    = False
    bump:                 bool    = False
    scream:               bool    = False
    safe:                 bool    = False

    def confounded_repr(self):return '%' if self.confounded else '.'
    def stench_repr(self): return '=' if self.stench else '.'
    def tingle_repr(self): return 'T' if self.tingle else '.'
    def NPC_repr(self): return '-' if self.portal or self.wumpus else ' '
    def glitter_repr(self): return '*' if self.glitter else '.'
    def bump_repr(self): return 'B' if self.bump else '.'
    def scream_repr(self): return '@' if self.scream else '.'
    
    def middle_cell(self):
        if self.portal and self.wumpus: return 'U'
        elif self.wumpus: return 'W'
        elif self.portal: return 'O'
        elif self.agent_direction: 
            if self.agent_direction == 'rnorth':   return '^'
            elif self.agent_direction == 'reast':  return  '>'
            elif self.agent_direction == 'rsouth': return 'v'
            elif self.agent_direction == 'rwest':  return  '<'
        elif self.safe:
            if self.visited: return 'S'
            else: return 's'
        else: return '?'
        
    def row_1(self):
        if self.wall: return "###"
        return f"{self.confounded_repr()}{self.stench_repr()}{self.tingle_repr()}"
    
    def row_2(self):
        if self.wall: return "###"
        return f"{self.NPC_repr()}{self.middle_cell()}{self.NPC_repr()}"
        
        
    def row_3(self):
        if self.wall: return "###"
        return f"{self.glitter_repr()}{self.bump_repr()}{self.scream_repr()}"
        
    def __str__(self):
        return f"{self.row_1()} {self.row_2()} {self.row_3()}"

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    pl = Prolog()
    pl.consult('prolog_agent/agent.pl')
    kbs = KnownWorld(prolog_interface=pl)
    
    i = 0
    # for move in ['turnright','moveforward','moveforward','moveforward','moveforward',
    # 'turnright','moveforward','moveforward','moveforward','moveforward']:
    for move in ['turnleft','moveforward']:
        print('-'*50)
        print(move)
        i += 1
        if i % 7 == 0:
            query_str = f'move({move},off,off,on,off,off,off).'
        else:
            query_str = f'move({move},off,off,off,off,off,off).'
        r = kbs.prolog_interface.query(query_str)
        list(r)
        
        
        kbs.update_world()
        kbs.print_map()
