# command registry

from typing import Callable, Any

##
## command registry
##

COMMANDS = {}
def register(func: Callable) -> Callable:
    COMMANDS[func.__name__] = func
    return func

##
## global config
##

class Config(dict):
    def __getattr__(self, key: str) -> Any:
        return super().__getitem__(key)
    def __setattr__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)
CONFIG = Config()
