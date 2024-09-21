import json
import os

if not os.path.exists("./cfg"): os.mkdir("./cfg")

def copy_missing_configs(source: str, dest: str):
    with open(source, 'r') as _s: infile = json.load(_s)
    
    try: 
        with open(dest, 'r') as _d: outfile = json.load(_d)
    except (json.JSONDecodeError, FileNotFoundError):
        # copy the file
        with open(dest, 'w') as _d: json.dump(infile, _d)
        return
    
    has_any_changed = False
    
    for key, value in infile.items():
        try:
            outfile[key]
        except KeyError:
            outfile[key] = value
            has_any_changed = True
    
    if has_any_changed:
        with open(dest, 'w') as _s: json.dump(outfile, _s)

copy_missing_configs("etc/defaults/cfg/config.json", "cfg/config.json")

class Config:
    def __init__(self, fp: str = "cfg/config.json"):
        with open(fp) as _infile:
            d = json.load(_infile)

        for key, value in d.items():
            setattr(self, key, value)

cfg = Config()

# Special config options
cfg.asset_folder = "./res"
cfg.floor_y = cfg.screen_height - cfg.screen_height * cfg.floor_y_ratio
cfg.scroll_speed = cfg.scroll_speed_ratio * cfg.screen_width
cfg.initial_aircraft_x = cfg.initial_aircraft_x_ratio * cfg.screen_width
cfg.initial_aircraft_y = cfg.initial_aircraft_y_ratio * cfg.screen_height