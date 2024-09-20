import json
import os

def copy_missing_configs(source: str, dest: str):
    with open(source, 'r') as _s: infile = json.load(_s)
    
    try: 
        with open(dest, 'r') as _d: outfile = json.load(_d)
    except (json.JSONDecodeError, FileNotFoundError):
        # copy the file
        with open(dest, 'w') as _d: json.dump(infile, _d)
        return
    
    for key, value in infile.items():
        try:
            outfile[key]
        except KeyError:
            outfile[key] = value
    
    with open(dest, 'w') as _s: json.dump(outfile, _s)

copy_missing_configs("etc/defaults/cfg/config.json", "cfg/config.json")

class Config:
    def __init__(self, fp: str = "cfg/config.json"):
        with open(fp) as _infile:
            d = json.load(_infile)

        for key, value in d.items():
            setattr(self, key, value)

cfg = Config()
