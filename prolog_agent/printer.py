
from dataclasses import dataclass, field
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
class KnownWorld:
    prolog_interface:  object
    agent:             PrologAgent = PrologAgent((0, 0), 'rnorth')
    visited:           list = field(default_factory=list)
    stench:            list = field(default_factory=list)
    tingle:            list = field(default_factory=list)
    wall:              list = field(default_factory=list)
    possibleWumpus:    list = field(default_factory=list)
    possibleConfundus: list = field(default_factory=list)
    
    wumpusAlive:       bool = True
    hasarrow:          bool = True
    numGoldCoins:      int  = 0
    
    def __post_init__(self) -> None:
        assert self.prolog_interface.query('printHunter.'), "Prolog interface to KBS printer not available"
        
        
    def create_map(self):
        max_x,max_y, min_x, min_y = 0,0,0,0
        for coord_grp in [self.visited, self.wall, self.possibleWumpus, self.possibleConfundus]:
            try:
                t_max_x, t_max_y = max(i[0] for i in coord_grp), max(i[1] for i in coord_grp)
                max_x = t_max_x if t_max_x > max_x else max_x
                max_y = t_max_y if t_max_y > max_y else max_y
                
                t_min_x, t_min_y = min(i[0] for i in coord_grp), min(i[1] for i in coord_grp)
                min_x = t_min_x if t_min_x > min_x else min_x
                min_y = t_min_y if t_min_y > min_y else min_y
            
            # list of self.wall etc. might be empty
            except ValueError:
                continue
        
        print(max_x,max_y)
            
        
        
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
    agent:      PrologAgent = None
    confounded: bool    = False
    stench:     bool    = False
    tingle:     bool    = False
    portal:     bool    = False
    wumpus:     bool    = False
    glitter:    bool    = False
    bump:       bool    = False
    scream:     bool    = False
    visited:    bool    = False
    safe:       bool    = False
    wall:       bool    = False

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
            elif self.agent.direction == 'rsouth': return '<'
            elif self.agent.direction == 'rwest': return 'v'
        elif self.safe:
            if self.visited: return 'S'
            else: return 's'
        else: return '?'
        
    def __str__(self):
        return f"{self.confounded_repr()}{self.stench_repr()}{self.tingle_repr()}\n\
{self.NPC_repr()}{self.middle_cell()}{self.NPC_repr()}\n\
{self.glitter_repr()}{self.bump_repr()}{self.scream_repr()}"
        
@dataclass
class EmptyMapCell:
        def __str__(self):
            return f"   \n   \n   "

if __name__ == "__main__":
    pl = Prolog()
    pl.consult('prolog_agent/agent.pl')
    kbs = KnownWorld(prolog_interface=pl)
    r = kbs.prolog_interface.query('explore(L).')
    moves = list(r)[0]['L']
    print(moves)
    
    for move in moves:
        print(move)
        query_str = f'move({move},off,off,off,off,off,off).'
        print(query_str)
        r = kbs.prolog_interface.query(query_str)
        
    kbs.update_world()
    kbs.create_map()