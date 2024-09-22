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
    
    for category, contents in infile.items():
        try:
            outfile[category]
        except KeyError:
            outfile[category] = contents
            has_any_changed = True
            continue

        for key, value in contents:
            try:
                outfile[category][key]
            except KeyError:
                outfile[category][key] = value
                has_any_changed = True
    
    if has_any_changed:
        with open(dest, 'w') as _s: json.dump(outfile, _s)

class ConfigCategory:
    def __init__(self) -> None:
        pass

class Config:
    def __init__(self, fp: str = "cfg/config.json"):
        with open(fp) as _infile:
            d = json.load(_infile)

        for category, contents in d.items():
            setattr(self, category, ConfigCategory())
            for key, value in contents.items():
                setattr(category, key, value)
                if key != "sprite_sizes" and key != "ui": # legacy support
                    setattr(self, key, value)


copy_missing_configs("etc/defaults/cfg/config.json", "cfg/config.json")
cfg = Config()

# Special config options
cfg.asset_folder = "./res"
cfg.floor_y = cfg.screen_height - cfg.screen_height * cfg.floor_y_ratio
cfg.scroll_speed = cfg.scroll_speed_ratio * cfg.screen_width
cfg.initial_aircraft_x = cfg.initial_aircraft_x_ratio * cfg.screen_width
cfg.initial_aircraft_y = cfg.initial_aircraft_y_ratio * cfg.screen_height