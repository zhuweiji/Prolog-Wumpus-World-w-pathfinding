
from dataclasses import dataclass, field
from importlib.machinery import BuiltinImporter
from pyswip import Prolog

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
    cells: list
    
    def size(self):
        return len(self.cells[0]), len(self.cells)
    
    def __str__(self) -> str:
        for row in self.cells:
            for cell in row:
                print(cell, end = "")
            print()
        return ''
    
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
    scream:            list = field(default_factory=list)
    safe:              list = field(default_factory=list)
    
    wumpusAlive:       bool = True
    hasarrow:          bool = True
    numGoldCoins:      int  = 0
    
    def __post_init__(self) -> None:
        assert self.prolog_interface.query('printHunter.'), "Prolog interface to KBS printer not available"
        
        
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
                    if attribute_name == 'bump': mapcell.bump = True
                    if attribute_name == 'scream': mapcell.scream = True
                    if attribute_name == 'safe': mapcell.safe = True
            elif attribute_name == 'agent':
                coords = attribute_value.coordinates
                print(f'agent coordinates: {coords}')
                if coords not in cells: cells[coords] = MapCell(coords=coords) 
                mapcell = cells[coords]
                mapcell.agent = attribute_value
        
        max_x,max_y, min_x, min_y = 0,0,0,0
        for mapcell in cells.values():
            coords = mapcell.coords
            if coords[0] > max_x: max_x = coords[0]
            if coords[1] > max_y: max_y = coords[1]
            if coords[0] < min_x: min_x = coords[0]
            if coords[1] < min_y: min_y = coords[1]
        
        print(max_x, max_y, min_x, min_y)
        map = []
        for yidx in range(min_y, max_y+1):
            row = []
            for xidx in range(min_x, max_x+1):
                coords = (xidx, yidx)
                if coords in cells:
                    cell = cells[coords]
                else:
                    cell = MapCell()
                    cells[coords] = MapCell()
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
        
        self.possibleWumpus = self.query_compound_coords("possibleWumpus")
        self.possibleConfundus = self.query_compound_coords("possibleConfundus")
        
        self.wumpusAlive = self.query_bool('wumpusAlive')
        self.hasarrow = self.query_bool('hasarrow')
        # self.numGoldCoins = self.query_bool('numGoldCoins')
        
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
                
    def query_first_solution(self, query):
        res = list(self.prolog_interface.query(query))
        if not res:
            return None
        return res[0]
    
@dataclass
class MapCell:
    coords:     tuple    = None
    agent:      PrologAgent = None
    confounded: bool    = False
    visited:    bool    = False
    stench:     bool    = False
    tingle:     bool    = False
    wall:       bool    = False
    glitter:    bool    = False
    wumpus:     bool    = False
    portal:     bool    = False
    bump:       bool    = False
    scream:     bool    = False
    safe:       bool    = False

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
        elif self.agent: 
            if self.agent.direction == 'rnorth': return '^'
            elif self.agent.direction == 'reast': return '>'
            elif self.agent.direction == 'rsouth': return 'v'
            elif self.agent.direction == 'rwest': return '<'
        elif self.safe:
            if self.visited: return 'S'
            else: return 's'
        else: return '?'
        
    def __str__(self):
        return f"{self.confounded_repr()}{self.stench_repr()}{self.tingle_repr()}\
{self.NPC_repr()}{self.middle_cell()}{self.NPC_repr()}\
{self.glitter_repr()}{self.bump_repr()}{self.scream_repr()}|"

    def __repr__(self):
        return self.__str__()
        
@dataclass
class EmptyMapCell:
        def __str__(self):
            return f"|   |\n|   |\n|   |"

if __name__ == "__main__":
    pl = Prolog()
    pl.consult('prolog_agent/agent.pl')
    kbs = KnownWorld(prolog_interface=pl)
    
    # r = kbs.prolog_interface.query('explore(L).')
    # moves = list(r)[0]['L']
    # print(moves)
    
    # for move in ['moveforward', 'turnleft','moveforward','moveforward','turnright','moveforward']:
    i = 0
    for move in ['turnright','moveforward','moveforward','moveforward','moveforward',
    'turnright','moveforward','moveforward','moveforward','moveforward']:
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
        for row in kbs.create_map():
            print(row)