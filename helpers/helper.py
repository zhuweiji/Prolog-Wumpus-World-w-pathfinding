from pathlib import Path

from helpers import config

wall_filepath = Path.cwd() / 'walls.pl'
print(wall_filepath)

def create_walls():
    map_size = config.MAP_SIZE
    x,y = map_size
    
    wall_code = [f"wall(0,{i})" for i in range(y+2)]
    wall_code = [*wall_code, *[f"wall({x+1},{i})" for i in range(y+2)]]
    wall_code = [*wall_code, *[f"wall({i},0)" for i in range(x+2)]]
    wall_code = [*wall_code, *[f"wall({i},{y+1})" for i in range(x+2)]]
    
    wall_code = list({k:0 for k in wall_code})
    
    # print(f"Adding wall code: {wall_code}")
    
    with open(wall_filepath, 'w+') as f:
        # print(f)
        for wall in wall_code:
            f.write(f"{wall}.")
            f.write('\n')
        
if __name__ == "__main__":
    create_walls()