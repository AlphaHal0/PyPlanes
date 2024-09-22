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

        for key, value in contents.items():
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

class ConfigLoadError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Config:
    def __init__(self, fp: str = "cfg/config.json"):
        self.fp = fp
        self.try_load()
            
    def try_load(self, only_once: bool = False):
        try: # try once
            self.load()
        except:
            if only_once: raise ConfigLoadError(e.args)
            
            try: # remove and try again
                if os.path.exists(self.fp): os.remove(self.fp)
                self.load()
            except Exception as e: # something's wrong
                raise ConfigLoadError(e.args)

    def load(self):
        copy_missing_configs(f"etc/defaults/{self.fp}", self.fp)

        with open(self.fp) as _infile:
            d = json.load(_infile)
        
        for category, contents in d.items():
            setattr(self, category, ConfigCategory())
            for key, value in contents.items():
                setattr(self.__getattribute__(category), key, value)
                if category != "sprite_sizes" and category != "ui": # legacy support
                    setattr(self, key, value)

        self.d = d

    def save(self):
        with open(self.fp, 'w') as _outfile:
            json.dump(self.d, _outfile)

    def set_value(self, category: str, key: str, value = None):
        self.d[category][key] = value
        setattr(self.__getattribute__(category), key, value)

        if category != "sprite_sizes" and category != "ui": # legacy support
            setattr(self, key, value)

    def toggle_value(self, category: str, key: str) -> bool|None:
        if self.d[category][key] == True:
            self.set_value(category, key, False)
            return False
        elif self.d[category][key] == False:
            self.set_value(category, key, True)
            return True
        else:
            return None
        
    def reset(self):
        if os.path.exists(self.fp): os.remove(self.fp)
        self.try_load(True)

cfg = Config("cfg/config.json")

# Special config options
cfg.asset_folder = "./res"
cfg.floor_y = cfg.screen_height - cfg.screen_height * cfg.floor_y_ratio
cfg.scroll_speed = cfg.scroll_speed_ratio * cfg.screen_width
cfg.initial_aircraft_x = cfg.initial_aircraft_x_ratio * cfg.screen_width
cfg.initial_aircraft_y = cfg.initial_aircraft_y_ratio * cfg.screen_height