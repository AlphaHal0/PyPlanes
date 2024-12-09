import json
import os

if not os.path.exists("./cfg"): os.mkdir("./cfg")

def copy_missing_configs(source: str, dest: str) -> bool:
    """Copies options from one file to another.
    If dest is missing, copies source to dest.
    Otherwise, reads through all config objects in source and copies over any objects that are not currently in dest.
    Returns False if dest had to be fully reset, else True"""
    with open(source, 'r') as _s: infile = json.load(_s)
    
    try: 
        with open(dest, 'r') as _d: outfile = json.load(_d)
    except (json.JSONDecodeError, FileNotFoundError):
        # copy the file
        print(f"[!] Reloading file {dest} from defaults")
        with open(dest, 'w') as _d: json.dump(infile, _d)
        return False
    
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

    return True

class ConfigCategory:
    """A class that handles a config category.
    Config initialises this class and manually sets attributes for it."""
    def __init__(self) -> None:
        pass

class ConfigLoadError(Exception):
    """Class to manage config load errors"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Config:
    """A class to manage a config from a json file.
    This file must be seperated into categories which each contain their own values."""
    def __init__(self, fp: str = "cfg/config.json"):
        self.fp = fp
        self.try_load()
            
    def try_load(self, only_once: bool = False) -> None:
        """Tries to load the config from self.fp. If it fails (and only_once is false) it resets the file and tries to load again.
        If that fails, raises ConfigLoadError"""
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
        """Loads contents from self.fp into the Config's attributes.
        Categories are seperated, e.g. {\"cat\":{\"myvalue:\":123}} becomes self.cat.myvalue = 123"""
        copy_missing_configs(f"etc/defaults/{self.fp}", self.fp)

        with open(self.fp) as _infile:
            d = json.load(_infile)
        
        for category, contents in d.items():
            setattr(self, category, ConfigCategory())
            for key, value in contents.items():
                setattr(getattr(self, category), key, value)

        self.d = d

    def save(self):
        """Saves contents into self.fp"""
        with open(self.fp, 'w') as _outfile:
            json.dump(self.d, _outfile)

    def set_value(self, category: str, key: str, value = None):
        """Sets a value in this Config"""
        self.d[category][key] = value
        setattr(self.__getattribute__(category), key, value)

    def toggle_value(self, category: str, key: str) -> bool|None:
        """If this config item is a bool, toggle it and return the new value.
        Otherwise, return None"""
        if self.d[category][key] == True:
            self.set_value(category, key, False)
            return False
        elif self.d[category][key] == False:
            self.set_value(category, key, True)
            return True
        else:
            return None
        
    def reset(self):
        """Removes the file at self.fp and tries to load it from defaults"""
        if os.path.exists(self.fp): os.remove(self.fp)
        self.try_load(True)

cfg = Config("cfg/config.json")

# Special config options
cfg.screen_height = cfg.display.screen_height
cfg.screen_width = cfg.display.screen_width
cfg.floor_y = cfg.screen_height - cfg.screen_height * cfg.display.floor_y_ratio
cfg.scroll_speed = cfg.display.scroll_speed_ratio * cfg.screen_width
cfg.initial_aircraft_x = cfg.display.initial_aircraft_x_ratio * cfg.screen_width
cfg.initial_aircraft_y = cfg.display.initial_aircraft_y_ratio * cfg.screen_height

kb = Config("cfg/keybinds.json")
