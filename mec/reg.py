# command registry

import os
import tomllib

from pathlib import Path
from typing import Callable, Any

##
## types
##

type Stdin = None

##
## config directory
##

XDG_HOME = Path(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')))
CONFIG_DIR = XDG_HOME / 'mec'

##
## global config
##

class Config(dict):
    def __getattr__(self, key: str) -> Any:
        return super().__getitem__(key)
    def __setattr__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)

# global config
with (CONFIG_DIR / 'cmd.toml').open('rb') as fid:
    cfg = tomllib.load(fid)
CONFIG = Config(**cfg)

##
## command registry
##

COMMANDS = {}
def register(func: Callable) -> Callable:
    COMMANDS[func.__name__] = func
    return func
